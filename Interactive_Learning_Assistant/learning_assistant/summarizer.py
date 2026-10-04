"""
summarizer.py
Abstractive + rule-based summarization with graceful fallbacks.
Outputs concise bullet points.
"""
from __future__ import annotations
from typing import List
import re

def _clean_bullets(bullets):
    cleaned = []
    for b in bullets:
        b = re.sub(r"\s+", " ", b).strip(" -•\n\t")
        if b and b not in cleaned:
            cleaned.append(b)
    return cleaned[:12]  # cap for brevity

def summarize_text(text: str, max_points: int = 6) -> List[str]:
    """
    Try transformers → fall back to Sumy/NLTK → fall back to simple heuristic.
    Always returns a list of short bullet points.
    """
    text = (text or "").strip()
    if not text:
        return []

    # Try Transformers (BART or T5)
    try:
        from transformers import pipeline
        try:
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception:
            summarizer = pipeline("summarization", model="t5-small")
        # Chunk long text for summarization
        chunks = _split_to_chunks(text, max_tokens=900)
        out = []
        for ch in chunks:
            s = summarizer(ch, max_length=130, min_length=25, do_sample=False)
            if isinstance(s, list) and s:
                out.append(s[0].get("summary_text", ""))
        bullets = _to_bullets(" ".join(out), max_points=max_points)
        if bullets:
            return _clean_bullets(bullets)
    except Exception:
        pass

    # Fall back to Sumy (LexRank / LSA)
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lex_rank import LexRankSummarizer

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        # select top n sentences
        summary_sents = summarizer(parser.document, max_points * 2)
        bullets = [str(s) for s in summary_sents]
        if bullets:
            return _clean_bullets(bullets[:max_points])
    except Exception:
        pass

    # Heuristic fallback: first N key sentences
    sents = _split_sentences(text)
    # prioritize sentences with dates/numbers/named entities-like patterns
    scored = []
    for s in sents:
        score = 0
        if re.search(r"\b(19|20)\d{2}\b", s): score += 2
        if re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December|\d{1,2}/\d{1,2}/\d{2,4})\b", s, re.I): score += 1
        if re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", s): score += 1
        score += min(3, len(s) // 80)
        scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], sents.index(x[1])))
    bullets = [s for _, s in scored[:max_points]]
    return _clean_bullets(bullets)

def _split_sentences(text: str):
    try:
        import nltk
        nltk.download("punkt", quiet=True)
        from nltk.tokenize import sent_tokenize
        return [s.strip() for s in sent_tokenize(text) if s.strip()]
    except Exception:
        return re.split(r"(?<=[.!?])\s+", text)

def _to_bullets(text: str, max_points: int = 6):
    # split summary into short bullet-like lines
    sents = _split_sentences(text)
    bullets = []
    for s in sents:
        s = s.strip()
        if len(s) > 140:
            # break on semicolons/commas to keep concise
            parts = re.split(r"[;:]\s+", s)
            bullets.extend([p.strip() for p in parts if len(p.strip()) >= 25])
        else:
            bullets.append(s)
    bullets = [b for b in bullets if 10 <= len(b) <= 180]
    return bullets[:max_points]

def _split_to_chunks(text: str, max_tokens: int = 900):
    # very rough "token" splitter by words
    words = text.split()
    chunk, chunks = [], []
    count = 0
    for w in words:
        chunk.append(w)
        count += 1
        if count >= max_tokens:
            chunks.append(" ".join(chunk))
            chunk, count = [], 0
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks
