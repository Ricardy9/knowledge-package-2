"""Write a small synthetic corpus about the fictional country of Riverland.

Used by the test suite and for a first trial run:
    python tests/fixtures/make_corpus.py inputs/corpus
Nothing here is real source material.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf
from docx import Document

ALPHA_PAGES = [
    ("11", "Riverland Annual Situation Report 2025\n"
           "57. Riverland recorded 1,642 displacement events in 2023.\n"
           "58. Flooding along the Blue Reed basin displaced 12,400 households."),
    ("12", "59. Customary courts resolved most cattle disputes in Northvale county.\n"
           "60. Grain prices rose 38 percent between March and June 2024."),
    ("13", "61. The 2021 assessment found weak budget execution.\n"
           "62. By 2025 budget execution had improved to 71 percent."),
]
BETA_PARAGRAPHS = [
    "Riverland Peace Brief 2024",
    "Women's peace committees mediated 14 local disputes in 2024.",
    "Mobile phone coverage reached 40 percent of rural districts.",
]


def _alpha_pdf(path: Path) -> None:
    doc = pymupdf.open()
    for folio, body in ALPHA_PAGES:
        page = doc.new_page()
        page.insert_text((72, 72), body, fontsize=11)
        page.insert_text((300, 800), folio, fontsize=10)
    doc.save(str(path))


def make_corpus(dest: Path) -> None:
    dest = Path(dest)
    (dest / "alpha").mkdir(parents=True, exist_ok=True)
    (dest / "beta").mkdir(parents=True, exist_ok=True)
    _alpha_pdf(dest / "alpha" / "alpha_report.pdf")
    (dest / "alpha" / "alpha_report_copy.pdf").write_bytes((dest / "alpha" / "alpha_report.pdf").read_bytes())
    docx = Document()
    for text in BETA_PARAGRAPHS:
        docx.add_paragraph(text)
    docx.save(str(dest / "beta" / "beta_brief.docx"))
    (dest / "beta" / "broken.pdf").write_bytes(b"%PDF-1.4 this is not a real pdf")


if __name__ == "__main__":
    make_corpus(Path(sys.argv[1] if len(sys.argv) > 1 else "inputs/corpus"))
