import json

from kp.ingest import doc_id_for, ingest, load_manifest, load_pages, page_label, pages_for, printed_folio
from kp.textutil import content_terms, normalize_for_match, score_window
from pathlib import Path


def test_printed_folio_takes_last_standalone_number():
    assert printed_folio("57. Text\n58. More\n11\n") == 11
    assert printed_folio("Report 2025\nno folio here") is None


def test_doc_id_is_stable_and_readable():
    assert doc_id_for(Path("alpha/Alpha Report.pdf")) == "alpha__alpha-report"


def test_content_terms_and_scoring():
    terms = content_terms("Grain prices rose 38 percent in 2024.")
    assert {"grain", "prices", "38", "2024", "percent"} <= terms
    assert "the" not in terms
    assert score_window({"grain", "38"}, "Grain rose 38 percent") == 3   # figures count double


def test_normalize_for_match_handles_quotes_dashes_and_hyphenation():
    assert normalize_for_match("“displace-\nment”  —  done") == '"displacement" - done'


def test_ingest_builds_manifest_with_duplicates_and_failures(corpus_project):
    docs = {d["doc_id"]: d for d in load_manifest(corpus_project)["documents"]}
    assert docs["alpha__alpha-report"]["status"] == "ok"
    assert docs["alpha__alpha-report"]["pages"] == 3
    assert docs["alpha__alpha-report-copy"]["status"] == "duplicate"
    assert docs["alpha__alpha-report-copy"]["duplicate_of"] == "alpha__alpha-report"
    assert docs["beta__broken"]["status"] == "failed" and docs["beta__broken"]["error"]
    assert docs["beta__beta-brief"]["collection"] == "beta"
    assert "README" not in json.dumps(docs)          # the folder README is not a source


def test_pages_carry_printed_folios(corpus_project):
    pages = load_pages(corpus_project, "alpha__alpha-report")
    assert [p["printed_page"] for p in pages] == [11, 12, 13]
    assert "12,400 households" in pages[0]["text"]
    assert page_label(pages[1]) == "12"
    assert pages_for(pages, "12") == [1]
    assert pages_for(pages, "pdf:3") == [2]
    beta = load_pages(corpus_project, "beta__beta-brief")
    assert page_label(beta[0]) == "pdf:1"


def test_reingest_skips_unchanged_files(corpus_project):
    summary = ingest(corpus_project)
    assert summary["unchanged"] == 2 and summary["ok"] == 0
