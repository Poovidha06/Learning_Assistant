"""
visualizer.py
Builds timelines, maps, and concept/flow graphs.
"""
from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import re
from datetime import datetime, timedelta

def parse_events(text: str) -> List[Tuple[str, datetime]]:
    """
    Extract (label, date) pairs from text. Very forgiving.
    """
    # Simple regex for years and day-month-year
    candidates = []
    # YYYY
    for m in re.finditer(r"\b((?:1[5-9]\d{2}|20\d{2}|21\d{2}))\b", text):
        year = int(m.group(1))
        dt = datetime(year, 1, 1)
        snippet = _sentence_containing(text, m.start(), m.end())
        label = _shorten(snippet or f"Event {year}")
        candidates.append((label, dt))
    # dd/mm/yyyy or dd-mm-yyyy
    for m in re.finditer(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", text):
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100: y += 2000
        try:
            dt = datetime(y, mo, d)
            snippet = _sentence_containing(text, m.start(), m.end())
            label = _shorten(snippet or f"{d}/{mo}/{y}")
            candidates.append((label, dt))
        except Exception:
            continue
    # Deduplicate by (label,year)
    seen = set()
    uniq = []
    for lab, dt in candidates:
        key = (lab, dt.year, dt.month, dt.day)
        if key not in seen:
            uniq.append((lab, dt))
            seen.add(key)
    # Sort by date
    uniq.sort(key=lambda x: x[1])
    return uniq[:20]

def make_timeline(events: List[Tuple[str, datetime]]):
    """
    Build a Plotly timeline figure. Each event is a 1-day bar.
    """
    if not events:
        return None
    try:
        import pandas as pd
        import plotly.express as px
        df = pd.DataFrame([{"Event": lab, "Start": dt, "Finish": dt + timedelta(days=1)} for lab, dt in events])
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Event")
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=500, margin=dict(l=10,r=10,t=30,b=10))
        return fig
    except Exception:
        return None

def make_map(locations: List[str]):
    """
    Build a Folium map from a list of location names. Attempts geocoding.
    """
    if not locations:
        return None
    try:
        import folium
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="interactive_learning_assistant")
        coords = []
        for name in locations[:10]:
            try:
                loc = geolocator.geocode(name, timeout=10)
                if loc:
                    coords.append((loc.latitude, loc.longitude, name))
            except Exception:
                continue
        if not coords:
            return None
        # center on mean
        lat = sum(c[0] for c in coords)/len(coords)
        lon = sum(c[1] for c in coords)/len(coords)
        m = folium.Map(location=[lat, lon], zoom_start=2)
        for la, lo, label in coords:
            folium.Marker([la, lo], popup=label).add_to(m)
        return m
    except Exception:
        return None

def make_flow(sentences: List[str]):
    """
    Create a simple flow diagram from sentence order.
    """
    if not sentences:
        return None
    try:
        from graphviz import Digraph
        g = Digraph(format="svg")
        g.attr(rankdir="LR", fontsize="10")
        for i, s in enumerate(sentences[:10]):
            g.node(f"n{i}", _shorten(s, 60), shape="rounded", style="filled", fillcolor="white")
            if i > 0:
                g.edge(f"n{i-1}", f"n{i}", label=f"step {i}")
        return g
    except Exception:
        return None

def make_concept_map(pairs: List[Tuple[str, str, str]]):
    """
    Build concept map from (subject, relation, object) triples.
    """
    if not pairs:
        return None
    try:
        from graphviz import Digraph
        g = Digraph(format="svg")
        g.attr(rankdir="TB", fontsize="10")
        for i, (subj, rel, obj) in enumerate(pairs[:15]):
            s_id, o_id = f"s{i}", f"o{i}"
            g.node(s_id, _shorten(subj, 30), shape="ellipse", style="filled", fillcolor="white")
            g.node(o_id, _shorten(obj, 30), shape="ellipse", style="filled", fillcolor="white")
            g.edge(s_id, o_id, label=_shorten(rel, 20))
        return g
    except Exception:
        return None

def triple_extract(text: str):
    """
    Naive SVO triple extractor using spaCy if available; regex fallback.
    """
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        triples = []
        for sent in doc.sents:
            subs = [w for w in sent if w.dep_ in ("nsubj", "nsubjpass")]
            verbs = [w for w in sent if w.pos_ == "VERB"]
            objs = [w for w in sent if w.dep_ in ("dobj", "pobj", "attr")]
            if subs and verbs and objs:
                triples.append((" ".join([s.text for s in subs]), verbs[0].lemma_, " ".join([o.text for o in objs])))
        return triples[:15]
    except Exception:
        # fallback: (first Word) - "related_to" - (second Word) per sentence
        triples = []
        for s in re.split(r"(?<=[.!?])\s+", text):
            toks = re.findall(r"[A-Za-z]{3,}", s)
            if len(toks) >= 2:
                triples.append((toks[0], "related_to", toks[1]))
        return triples[:10]

def _sentence_containing(text, start, end):
    left = text.rfind(".", 0, start)
    right = text.find(".", end)
    if left == -1: left = 0
    else: left += 1
    if right == -1: right = len(text)
    return text[left:right].strip()

def _shorten(s: str, n: int = 80):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n-1] + "…"
