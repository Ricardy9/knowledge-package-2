"""Text helpers shared by search, evidence checks and verification.

Ported from the pilot's citation-audit tools (`excerpt.py`), without the
corpus-specific citation matching.
"""
import re

STOP = set("""the and for that with from this have has had been were was are its into
their they them then than when where which while about over under after before since
also more most such other others some many much both each between among against
during through across per said says will would could should may might must not but
his her our your there here what who whom whose why how all any few own same too very
can cell page report annex figure table""".split())

_NUM = re.compile(r"\d[\d,.]*%?")
_WORD = re.compile(r"[A-Za-z][A-Za-z'-]{3,}")
_TRANSLATE = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                            "–": "-", "—": "-", "­": "", " ": " "})


def content_terms(text: str) -> set[str]:
    """Terms whose presence in a passage indicates it bears on the text."""
    low = (text or "").casefold()
    terms = {t.strip(".,") for t in _NUM.findall(low) if t.strip(".,")}
    terms |= {w for w in _WORD.findall(low) if w not in STOP}
    return terms


def is_figure(term: str) -> bool:
    return bool(term) and term[0].isdigit()


def score_window(terms, window: str) -> int:
    """Figures weigh double: restated numbers are what citation checks exist to catch."""
    low = (window or "").casefold()
    return sum(2 if is_figure(t) else 1 for t in terms if t in low)


def normalize_for_match(text: str) -> str:
    """Normalize quote characters, dashes, soft hyphens, line-break hyphenation and
    whitespace. Words themselves are never changed."""
    t = (text or "").translate(_TRANSLATE)
    t = re.sub(r"-\s*\n\s*", "", t)
    return re.sub(r"\s+", " ", t).strip()
