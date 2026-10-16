"""`python -m kp <command>`: the Knowledge Package 2.0 runner."""
from __future__ import annotations

import argparse
import sys

from kp import __version__
from kp.config import ConfigError, load_config
from kp.ingest import IngestError
from kp.issues import has_errors, render
from kp.ledger import LedgerError
from kp.verify import VerifyError
from kp.questions import PackError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m kp", description=__doc__)
    p.add_argument("--version", action="version", version=f"kp {__version__}")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("init", help="create the folder skeleton and seed files (never overwrites)")
    sub.add_parser("ingest", help="extract text from inputs/corpus into package/.index")
    s = sub.add_parser("search", help="search the ingested corpus; prints passages with locators")
    s.add_argument("query")
    s.add_argument("--collection", default=None, help="limit to one collection ('*' = all)")
    s.add_argument("--k", type=int, default=5)
    s.add_argument("--json", action="store_true", help="machine-readable output")
    q = sub.add_parser("questions", help="Question Bank commands")
    q.add_argument("action", choices=["check"])
    pk = sub.add_parser("pack", help="write today's query pack from the Question Bank")
    pk.add_argument("--n", type=int, default=None, help="override [pack] size")
    ev = sub.add_parser("evidence", help="Evidence Record commands")
    ev.add_argument("action", choices=["check"])
    lg = sub.add_parser("ledger", help="Evidence Ledger commands")
    lg.add_argument("action", choices=["check"])
    lg.add_argument("--draft", action="store_true", help="also check draft markers against the ledger")
    vf = sub.add_parser("verify", help="independent citation verification")
    vf.add_argument("action", choices=["build", "collect"])
    vf.add_argument("--force", action="store_true", help="archive the current round and rebuild")
    return p


def report(issues) -> int:
    print(render(issues))
    return 1 if has_errors(issues) else 0


def dispatch(args, cfg) -> int:
    if args.command == "init":
        from kp.config import find_root
        from kp.init import init_project
        created = init_project(find_root())
        print("\n".join(f"created {c}" for c in created) or "nothing to create: project already initialised")
        return 0
    if args.command == "ingest":
        from kp.ingest import ingest, load_manifest
        counts = ingest(cfg)
        for d in load_manifest(cfg)["documents"]:
            if d["status"] in ("failed", "unsupported", "duplicate"):
                extra = d["error"] or f"same file as {d['duplicate_of']}"
                print(f"{d['status'].upper():11} {d['path']}: {extra}")
        print("ingest: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
        return 0
    if args.command == "search":
        import json as _json
        from kp.search import locator, search_corpus
        hits = search_corpus(cfg, args.query, collection=args.collection, k=args.k)
        if args.json:
            print(_json.dumps(hits, indent=2, ensure_ascii=False))
        elif not hits:
            print("no passages found: NOT FOUND IN SOURCES for this query")
        else:
            for h in hits:
                print(f"[{h['score']}] {locator(h)}\n    {h['quote']}\n")
        return 0
    if args.command == "questions":
        from kp.questions import check_bank, load_bank
        return report(check_bank(cfg, load_bank(cfg)))
    if args.command == "pack":
        from kp.questions import build_pack, load_bank
        md, js = build_pack(cfg, load_bank(cfg), n=args.n)
        print(f"wrote {md.relative_to(cfg.root).as_posix()} and {js.name}")
        return 0
    if args.command == "evidence":
        from kp.evidence import check_evidence
        return report(check_evidence(cfg))
    if args.command == "ledger":
        from kp.ledger import check_drafts, check_ledger, load_ledger
        rows = load_ledger(cfg)
        issues = check_ledger(cfg, rows)
        if args.draft:
            issues += check_drafts(cfg, rows)
        return report(issues)
    if args.command == "verify":
        from kp.verify import build, collect
        if args.action == "build":
            paths = build(cfg, force=args.force)
            print(f"wrote {len(paths)} batch file(s) to package/06_working_drafts/verification/batches/")
            print("next: grade each batch with instructions/prompts/verify_grader.md, then `python -m kp verify collect`")
            return 0
        summary = collect(cfg)
        print(f"verified {summary['items']} citation(s): {summary['actions']}; rejected verdicts: {summary['rejected']}")
        print("worklist: package/06_working_drafts/verification/worklist.csv")
        return 0
    raise SystemExit(f"unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        cfg = None if args.command in ("init", "check") else load_config()
        return dispatch(args, cfg)
    except (ConfigError, IngestError, PackError, LedgerError, VerifyError) as exc:
        print(f"ERROR   config: {exc}", file=sys.stderr)
        return 1
