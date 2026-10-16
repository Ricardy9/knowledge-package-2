# Advanced: the Python runner (optional)

**You do not need this folder to use the starter kit.** It is an optional tool for technical users who want automatic checks: it extracts text from PDFs, searches documents with page numbers, and verifies that every quote in an answer appears word for word on the page it cites.

To use it you need Python 3.11 or later. From this folder:

    python -m venv .venv
    .venv/Scripts/python -m pip install -r requirements.txt   # Mac/Linux: .venv/bin/python
    .venv/Scripts/python -m pytest -q
    .venv/Scripts/python -m kp --help
