"""
nlp_utils.py
Entity extraction, sentence simplification, and keyword extraction with fallbacks.
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import re
from collections import Counter

def get_nlp():
    # Try spaCy first
    try:
        import spacy
        try:
            return spacy.load("en_core_web_sm")
        except Exception:
            # try to download at runtime, may fail without internet
            try:
                from spacy.cli import download
                download("en_core_web_sm")
                import spacy as _sp
                return _sp.load("en_core_web_sm")
            except Exception:
                return None
    except Exception:
        return None

_NLP = None

def _nlp():
    global _NLP
    if _NLP is None:
        _NLP = get_nlp()
    return _NLP

def extract_entities(text: str) -> Dict[str, List[str]]:
    ents = {"PERSON": [], "ORG": [], "GPE": [], "DATE": [], "NORP": [], "LOC": [], "CARDINAL": []}
    nlp = _nlp()
    if nlp:
        doc = nlp(text)
        for e in doc.ents:
            label = e.label_
            if label in ents:
                ents[label].append(e.text)
    else:
        # Regex-based lightweight fallback
        ents["DATE"] = re.findall(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|(19|20)\d{2}|January|February|March|April|May|June|July|August|September|October|November|December)\b", text, flags=re.I)
        ents["CARDINAL"] = re.findall(r"\b\d+(?:\.\d+)?\b", text)
        # Proper names approximation
        ents["PERSON"] = re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)
        ents["GPE"] = []
        ents["ORG"] = []
        ents["LOC"] = []
        ents["NORP"] = []
    # dedupe + clean
    for k,v in ents.items():
        dedup = []
        for item in v:
            s = str(item).strip()
            if s and s not in dedup:
                dedup.append(s)
        ents[k] = dedup[:25]
    return ents

def keywords(text: str, top_k: int = 12) -> List[str]:
    # Try YAKE
    try:
        import yake
        kw_extractor = yake.KeywordExtractor(n=1, top=top_k)
        kws = [k for k, _ in kw_extractor.extract_keywords(text)]
        return _clean_terms(kws)
    except Exception:
        pass
    # Try RAKE
    try:
        from rake_nltk import Rake
        import nltk
        nltk.download("stopwords", quiet=True)
        r = Rake()
        r.extract_keywords_from_text(text)
        kws = r.get_ranked_phrases()[:top_k]
        return _clean_terms(kws)
    except Exception:
        pass
    # Fallback: most common nouns-ish tokens
    tokens = re.findall(r"[A-Za-z]{3,}", text)
    common = [w.lower() for w,_ in Counter(tokens).most_common(top_k*2)]
    return _clean_terms(common)[:top_k]

def _clean_terms(terms: List[str]) -> List[str]:
    cleaned = []
    for t in terms:
        t = re.sub(r"\s+", " ", t).strip(" .,-").lower()
        if t and t not in cleaned and len(t) <= 30:
            cleaned.append(t)
    return cleaned

def simple_sentences(text: str, max_len: int = 160) -> List[str]:
    # naive split + trimming for readability
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    simp = []
    for p in parts:
        p = p.strip()
        if 0 < len(p) <= max_len:
            simp.append(p)
        elif len(p) > max_len:
            # break long ones on commas/semicolons
            sub = re.split(r"[;:,\-]\s+", p)
            for s in sub:
                s = s.strip()
                if 0 < len(s) <= max_len:
                    simp.append(s)
    return simp[:50]
