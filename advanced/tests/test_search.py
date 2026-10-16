from kp.search import locator, search_corpus, search_pages


def test_search_pages_returns_printed_page_and_paragraph(corpus_project):
    from kp.ingest import load_pages
    hits = search_pages("grain prices rose 38 percent", load_pages(corpus_project, "alpha__alpha-report"))
    assert hits, "expected a hit"
    assert hits[0]["printed_page"] == 12
    assert hits[0]["paragraph"] == 60
    assert "38 percent" in hits[0]["quote"]


def test_search_corpus_filters_by_collection_and_skips_duplicates(corpus_project):
    hits = search_corpus(corpus_project, "peace committees mediated disputes", collection="beta")
    assert hits and all(h["collection"] == "beta" for h in hits)
    assert locator(hits[0]) == "beta__beta-brief, p. pdf:1"
    everywhere = search_corpus(corpus_project, "flooding Blue Reed households")
    assert {h["doc_id"] for h in everywhere} == {"alpha__alpha-report"}


def test_search_with_no_meaningful_terms_returns_nothing(corpus_project):
    assert search_corpus(corpus_project, "the and of") == []
