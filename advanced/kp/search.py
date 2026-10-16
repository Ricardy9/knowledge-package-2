"""Whole-document lexical search returning citable locations.

Ported from the pilot's `locate.py`. Searching whole documents, not pre-cut windows,
fixed the pilot's false negatives. Locations use printed folios because that is what
citations cite.
"""
from __future__ import annotations

import re

from kp.ingest import load_manifest, load_pages, page_label
from kp.textutil import content_terms, score_window

_PARA = re.compile(r"(?m)^\s*(\d{1,3})\.\s")


def _paragraph_at(text: str, offset: int) -> int | None:
    hits = list(_PARA.finditer(text[: max(offset, 0) + 1]))
    return int(hits[-1].group(1)) if hits else None


def _anchor(terms, text: str, start: int, size: int) -> int:
    """Median offset of the query's own terms in the window, so a window that opens on
    the previous page or paragraph is credited to where the words actually are."""
    window = text[start:start + size].casefold()
    hits = []
    for term in terms:
        at = window.find(term)
        while at != -1:
            hits.append(start + at)
            at = window.find(term, at + 1)
    if not hits:
        return start
    hits.sort()
    return hits[len(hits) // 2]


def search_pages(query: str, pages: list[dict], k: int = 3, size: int = 700, floor: int = 2) -> list[dict]:
    terms = content_terms(query)
    if not terms or not pages:
        return []
    text = "\f".join(p["text"] for p in pages)
    step = max(size // 3, 1)
    scored = []
    for start in range(0, max(len(text) - size, 0) + 1, step):
        s = score_window(terms, text[start:start + size])
        if s >= floor:
            scored.append((s, start))
    scored.sort(key=lambda t: (-t[0], t[1]))
    out, taken = [], []
    for s, start in scored:
        if any(abs(start - t) < size for t in taken):
            continue
        taken.append(start)
        off = _anchor(terms, text, start, size)
        page = pages[min(text.count("\f", 0, off), len(pages) - 1)]
        out.append({"pdf_page": page["pdf_page"], "printed_page": page["printed_page"],
                    "paragraph": _paragraph_at(text, off), "score": s,
                    "quote": re.sub(r"\s+", " ", text[start:start + size]).strip()})
        if len(out) == k:
            break
    return out


def search_corpus(cfg, query: str, collection: str | None = None, k: int = 5) -> list[dict]:
    hits = []
    for doc in load_manifest(cfg)["documents"]:
        if doc["status"] != "ok":
            continue
        if collection and collection != "*" and doc["collection"] != collection:
            continue
        for hit in search_pages(query, load_pages(cfg, doc["doc_id"]), k=2):
            hit.update(doc_id=doc["doc_id"], collection=doc["collection"])
            hits.append(hit)
    hits.sort(key=lambda h: (-h["score"], h["doc_id"], h["pdf_page"]))
    return hits[:k]


def locator(hit: dict) -> str:
    text = f"{hit['doc_id']}, p. {page_label(hit)}"
    if hit.get("paragraph") is not None:
        text += f", para {hit['paragraph']}"
    return text
