"""
quiz_generator.py
NER + keywords to generate MCQ, T/F, Fill-in-the-blank, and Short Answer.
"""
from __future__ import annotations
from typing import List, Dict
import random, re
from nlp_utils import extract_entities, keywords, simple_sentences

def generate_quiz(text: str, mcq_n=4, tf_n=3, fib_n=3, short_n=2) -> List[Dict]:
    ents = extract_entities(text)
    kw = keywords(text, top_k=20)
    sents = simple_sentences(text)

    questions = []
    # MCQs using PERSON/DATES/GPE facts
    pool_person = ents.get("PERSON", [])
    pool_gpe = ents.get("GPE", []) or ents.get("LOC", [])
    pool_date = ents.get("DATE", [])

    # MCQ: Who did X? (use sentence containing person name)
    for name in pool_person[:mcq_n]:
        sent = _sentence_with(sents, name)
        if not sent: continue
        q = re.sub(re.escape(name), "_____", sent)
        distractors = random.sample([p for p in pool_person if p != name], k=min(3, max(0, len(pool_person)-1))) or ["Unknown A","Unknown B","Unknown C"]
        options = distractors[:3] + [name]
        random.shuffle(options)
        questions.append({"type":"MCQ","question":q,"options":options,"answer":name,"explanation":sent})

    # MCQ: When did X happen?
    for d in pool_date[:max(0, mcq_n - len([q for q in questions if q['type']=='MCQ']))]:
        sent = _sentence_with(sents, d)
        if not sent: continue
        q = re.sub(re.escape(d), "_____", sent)
        # fabricate year-like distractors
        options = _year_distractors(d)
        questions.append({"type":"MCQ","question":q,"options":options,"answer":d,"explanation":sent})

    # True/False: mutate a sentence slightly
    for i in range(tf_n):
        if not sents: break
        base = random.choice(sents)
        mutated = _mutate_sentence(base)
        answer = "True" if mutated == base else "False"
        questions.append({"type":"True/False","question":mutated,"answer":answer,"explanation":base})

    # Fill in the blank using keywords
    for term in kw[:fib_n]:
        sent = _sentence_with(sents, term)
        if not sent: continue
        blanked = re.sub(re.escape(term), "_____", sent, flags=re.I)
        if blanked != sent:
            questions.append({"type":"Fill-in-the-blank","question":blanked,"answer":term,"explanation":sent})

    # Short answer from remaining sentences
    for s in sents[:short_n]:
        questions.append({"type":"Short answer","question":f"Briefly explain: {s}","answer":"","explanation":"Open response."})

    random.shuffle(questions)
    return questions[: mcq_n + tf_n + fib_n + short_n]

def _sentence_with(sents: List[str], term: str):
    term_re = re.compile(re.escape(term), re.I)
    for s in sents:
        if term_re.search(s):
            return s
    return ""

def _mutate_sentence(s: str) -> str:
    # Replace a named entity-like token
    toks = re.findall(r"\b[A-Z][a-z]+\b", s)
    if toks:
        s = re.sub(re.escape(toks[0]), random.choice(["Alex","Jordan","Taylor","Morgan"]), s, count=1)
        return s
    # flip a year
    y = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", s)
    if y:
        year = int(y.group(1))
        alt = str(year + random.choice([-3,-1,1,2,5]))
        return s.replace(str(year), alt, 1)
    return s

def _year_distractors(correct: str) -> List[str]:
    # produce year-like options
    ys = re.findall(r"(1[5-9]\d{2}|20\d{2})", correct)
    if ys:
        y = int(ys[0])
        options = {str(y + d) for d in [-7,-3,0,5]}
        return list(options)
    # otherwise recycle
    base = ["1492","1776","1914","1947"]
    if correct not in base:
        base.append(correct)
    random.shuffle(base)
    return base[:4]
