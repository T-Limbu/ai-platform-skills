#!/usr/bin/env python3
"""Check a repo's docs/ folder against the project-docs convention.

Usage:
  python check_docs.py REPO_ROOT                  # text report
  python check_docs.py REPO_ROOT --format github  # CI annotations
  python check_docs.py --help

Checks:
  index     every .md under docs/ (except INDEX.md, PROGRESS.md and progress/)
            is listed in docs/INDEX.md
  links     relative Markdown links in docs/ resolve (code fences are skipped)
  stamp     each topic doc has a "Verified against `<sha>`" stamp (the first
            backticked sha on the line after "verified" is this repo's) and the sha
            exists in the repo; a bare "verified" without a sha is a warning;
            more than STALE_COMMITS commits since the sha on the files the doc
            names is a warning
  progress  docs/PROGRESS.md has at most 10 entries ("## YYYY-MM-DD ..."
            headings), each at most 10 non-blank lines under its heading

Errors and warnings are printed separately. Exit code: 0 clean or warnings
only, 1 on any error, 2 on usage errors. Standard library only.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

STALE_COMMITS = 50
MAX_ENTRIES = 10
MAX_ENTRY_LINES = 10

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
# "Verified against `abc1234`" or "Verified against this repo at `abc1234`":
# the first backticked sha within the same line after "verified".
STAMP_RE = re.compile(r"verified\b[^\n`]{0,60}`([0-9a-f]{7,40})`", re.I)
VERIFIED_RE = re.compile(r"\bverified\b", re.I)
ENTRY_RE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\b")
NAMED_PATH_RE = re.compile(r"`([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]+)(?::\d+)?`")
EXEMPT_STAMP = {"INDEX.md", "PROGRESS.md"}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, line, msg):
        self.errors.append((path, line, msg))

    def warn(self, path, line, msg):
        self.warnings.append((path, line, msg))


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True)
    except OSError:
        return None
    return r


def _is_git_repo(root):
    r = _git(root, "rev-parse", "--is-inside-work-tree")
    return r is not None and r.returncode == 0 and r.stdout.strip() == "true"


def doc_files(docs):
    out = []
    for dirpath, dirnames, filenames in os.walk(docs):
        dirnames.sort()
        for f in sorted(filenames):
            if f.lower().endswith(".md"):
                out.append(os.path.join(dirpath, f))
    return out


def in_progress_dir(docs, path):
    rel = os.path.relpath(path, docs).replace(os.sep, "/")
    return rel.startswith("progress/")


def strip_fences(text):
    """Yield (line_number, line) outside fenced code blocks."""
    fence = None
    for i, line in enumerate(text.splitlines(), 1):
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            mark = s[:3]
            if fence is None:
                fence = mark
            elif fence == mark:
                fence = None
            continue
        if fence is None:
            yield i, line


def check_index(root, docs, files, rep):
    index = os.path.join(docs, "INDEX.md")
    if not os.path.isfile(index):
        rep.error(_rel(root, docs), 1, "docs/INDEX.md is missing")
        return
    text = _read(index)
    for p in files:
        if p == index or in_progress_dir(docs, p) or os.path.dirname(p) == docs and os.path.basename(p) == "PROGRESS.md":
            continue
        rel_docs = os.path.relpath(p, docs).replace(os.sep, "/")
        rel_root = _rel(root, p)
        if rel_docs not in text and rel_root not in text:
            rep.error(rel_root, 1, "not listed in docs/INDEX.md")


def check_links(root, files, rep):
    for p in files:
        for ln, line in strip_fences(_read(p)):
            for target in LINK_RE.findall(CODE_SPAN_RE.sub("", line)):
                if re.match(r"^[a-z][a-z0-9+.\-]*:", target, re.I) or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0].split("?", 1)[0]
                if not path:
                    continue
                dest = os.path.normpath(os.path.join(os.path.dirname(p), path))
                if not os.path.exists(dest):
                    rep.error(_rel(root, p), ln, "broken relative link: %s" % target)


def check_stamps(root, docs, files, rep, git_ok):
    for p in files:
        name = os.path.basename(p)
        if in_progress_dir(docs, p) or (os.path.dirname(p) == docs and name in EXEMPT_STAMP):
            continue
        rp = _rel(root, p)
        text = _read(p)
        m = STAMP_RE.search(text)
        if not m:
            if VERIFIED_RE.search(text):
                rep.warn(rp, 1, "'verified' stamp has no commit sha (use: Verified against `<sha>`)")
            else:
                rep.error(rp, 1, "no verified stamp (add: Verified against `<sha>`, date)")
            continue
        sha = m.group(1)
        line = text[:m.start()].count("\n") + 1
        if not git_ok:
            rep.warn(rp, line, "not a git repo or git unavailable; cannot check sha %s" % sha)
            continue
        r = _git(root, "cat-file", "-e", sha + "^{commit}")
        if r is None or r.returncode != 0:
            rep.error(rp, line, "verified sha %s does not exist in this repo" % sha)
            continue
        named = sorted({n for n in NAMED_PATH_RE.findall(text) if os.path.isfile(os.path.join(root, n))})
        if not named:
            continue
        r = _git(root, "rev-list", "--count", sha + "..HEAD", "--", *named)
        if r is not None and r.returncode == 0:
            count = int(r.stdout.strip() or 0)
            if count > STALE_COMMITS:
                rep.warn(rp, line, "%d commits since %s touch the files this doc names (re-verify)" % (count, sha))


def check_progress(root, docs, rep):
    p = os.path.join(docs, "PROGRESS.md")
    if not os.path.isfile(p):
        return
    rp = _rel(root, p)
    entries = []
    for ln, line in enumerate(_read(p).splitlines(), 1):
        if ENTRY_RE.match(line):
            entries.append([ln, 0])
        elif line.startswith("#"):
            if entries and line.startswith("## "):
                entries.append([ln, None])  # a non-dated level-2 heading ends the entry
        elif line.strip() and entries and entries[-1][1] is not None:
            entries[-1][1] += 1
    dated = [e for e in entries if e[1] is not None]
    if len(dated) > MAX_ENTRIES:
        rep.error(rp, dated[MAX_ENTRIES][0], "%d entries (keep the latest %d; move older ones to docs/progress/<year>.md)" % (
            len(dated), MAX_ENTRIES))
    for ln, count in dated:
        if count > MAX_ENTRY_LINES:
            rep.error(rp, ln, "entry has %d lines (limit %d)" % (count, MAX_ENTRY_LINES))


def run(root):
    rep = Report()
    docs = os.path.join(root, "docs")
    if not os.path.isdir(docs):
        rep.error("docs", 1, "no docs/ folder")
        return rep
    files = doc_files(docs)
    check_index(root, docs, files, rep)
    check_links(root, files, rep)
    check_stamps(root, docs, files, rep, _is_git_repo(root))
    check_progress(root, docs, rep)
    return rep


def print_report(rep, fmt, out=None):
    out = out or sys.stdout
    if fmt == "github":
        for path, line, msg in rep.errors:
            print("::error file=%s,line=%d::%s" % (path, line, msg), file=out)
        for path, line, msg in rep.warnings:
            print("::warning file=%s,line=%d::%s" % (path, line, msg), file=out)
        return
    if rep.errors:
        print("Errors:", file=out)
        for path, line, msg in rep.errors:
            print("  ERROR %s:%d  %s" % (path, line, msg), file=out)
    if rep.warnings:
        print("Warnings:", file=out)
        for path, line, msg in rep.warnings:
            print("  WARN  %s:%d  %s" % (path, line, msg), file=out)
    print("docs check: %d error(s), %d warning(s)" % (len(rep.errors), len(rep.warnings)), file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a repo's docs/ folder against the project-docs convention.")
    ap.add_argument("repo_root", help="path to the repository root (the folder that holds docs/)")
    ap.add_argument("--format", choices=["text", "github"], default="text", help="output format (default: text)")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.repo_root)
    if not os.path.isdir(root):
        print("error: %s is not a directory" % args.repo_root, file=sys.stderr)
        return 2
    rep = run(root)
    print_report(rep, args.format)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
