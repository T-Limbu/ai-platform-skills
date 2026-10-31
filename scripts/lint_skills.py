#!/usr/bin/env python3
"""Lint SKILL.md skills against the tool-neutral standard (checks L1-L19).

Usage:
  python scripts/lint_skills.py [PATH ...]            # default: repo root
  python scripts/lint_skills.py --format github       # CI annotations
  python scripts/lint_skills.py --format json
  python scripts/lint_skills.py --base origin/main    # L16 version-bump check
  python scripts/lint_skills.py --strict-version      # missing version is FAIL
  python scripts/lint_skills.py --no-yaml             # force built-in parser

Each skill is reported PASS, WARN or FAIL with file:line reasons. The exit
code is 1 when any skill has a FAIL (2 on usage errors). Matched secret text
is never printed: only the secret type and the file:line.

There is deliberately no exemption mechanism (no per-tool or per-line ignore).
Requires Python 3.9+. PyYAML is used when installed; otherwise a built-in
parser handles plain, quoted and folded/literal block scalars, nested maps
and simple lists.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

try:  # optional
    import yaml as _yaml
except Exception:  # pragma: no cover
    _yaml = None

IGNORE_DIRS = {".git", ".github", ".hg", ".svn", "node_modules", "__pycache__",
               ".venv", "venv", ".tox", ".mypy_cache", ".pytest_cache"}

# Size budget (standard section 4; owner decisions: target 200, WARN 300/9KB,
# FAIL over 400 lines / 12 KB).
BODY_TARGET_LINES = 200
BODY_WARN_LINES, BODY_FAIL_LINES = 300, 400
BODY_WARN_BYTES, BODY_FAIL_BYTES = 9 * 1024, 12 * 1024
REF_FAIL_LINES = 1500
DESC_WARN, DESC_FAIL = 500, 1024
FOLDER_WARN, FOLDER_FAIL = 100 * 1024, 500 * 1024

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
TRIGGER_RE = re.compile(r"\buse (when|whenever)\b", re.I)
ANGLE_RE = re.compile(r"[<>]")
FIRST_PERSON_RE = re.compile(r"\bI\b|\b(?:my|you|your)\b", re.I)

ALLOWED_KEYS = {"name", "description", "version", "license"}
VENDOR_KEYS = {"allowed-tools", "allowed_tools", "model", "tools", "hooks"}

# L6 vendor tool-call names
L6_RE = re.compile(
    r"\b(run_shell_command|ask_question|read_file|write_file|replace_in_file|"
    r"list_directory|google_web_search|web_fetch|save_memory|activate_skill|"
    r"codebase_investigator|invoke_subagent|view_file|run_command|search_web|"
    r"TodoWrite|AskUserQuestion|NotebookEdit|WebFetch|WebSearch|mcp__\w+)\b",
    re.I)
# L7 model names and tiers
L7_RES = [
    re.compile(r"\b(gemini[-\s]?[\d.]*\w*|flash[-_ ]?lite|gemini\s+(?:flash|pro)|"
               r"claude|sonnet|opus|haiku|gpt[-\s]?\d\w*|o[134]-\w+|codex)\b", re.I),
    re.compile(r"`(?:flash|flash_lite|pro)`", re.I),
    re.compile(r'"Model"\s*:\s*"'),
]
# L8 host product as actor. Bare "cursor" is not matched (CSS property, mouse
# cursor and text cursor are far more common); the editor is matched by its
# typical forms only: "Cursor IDE/editor/CLI/agent/rules", .cursorrules, .cursor/.
L8_RE = re.compile(
    r"(?<![-\w])(antigravity|jetski|agentapi|gemini[- ]cli|claude[- ]code|windsurf|copilot|"
    r"cursor[ -](?:ide|editor|cli|agent|rules)|\.?cursorrules|\.cursor/)(?![-\w])", re.I)
# L9 absolute machine paths
L9_RES = [
    re.compile(r"\b[A-Za-z]:[\\/](?:Users|Python\d+|Program Files)", re.I),
    re.compile(r"(?<![\w./:~-])/(?:Users|home)/[^/\s`'\"]+/"),
    re.compile(r"\\\\[\w.-]+\\[\w$]+"),
    re.compile(r"%USERPROFILE%\\Desktop", re.I),
]
# L10 secrets: (type name, regex). Only the type is ever printed.
L10_RES = [
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36}\b")),
    ("GitHub fine-grained token", re.compile(r"github_pat_[A-Za-z0-9_]{22,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("sk- style API key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]+")),
    ("credential assignment",
     re.compile(r"(?i)(api[_-]?key|token|secret|password)[\"']?\s*[:=]\s*[\"'][^\"'<>$\s]{12,}[\"']")),
]
PLACEHOLDER_RE = re.compile(
    r"x{4,}|example|your|placeholder|redacted|changeme|dummy|fake|\*{3,}|\.\.\.|"
    r"process\.env|os\.environ|getenv", re.I)

LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")
TICK_PATH_RE = re.compile(r"`((?:\./)?(?:scripts|references|assets)/[^`\s]*)`")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
EMOJI_RE = re.compile("[⌀-⏿☀-➿⬀-⯿️"
                      "\U0001f000-\U0001faff]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
# L19 skill references: `name` skill, or skill `name`; optional `plugin:` prefix.
_SKILL_REF = r"`(?:([a-z0-9-]+):)?([a-z0-9]+(?:-[a-z0-9]+)*)`"
L19_RES = [re.compile(_SKILL_REF + r" skill\b"), re.compile(r"\bskills? " + _SKILL_REF)]

TEXT_SCRIPT_EXT = {".py", ".sh", ".ps1", ".js", ".mjs", ".ts", ".bat", ".cmd",
                   ".json", ".yml", ".yaml", ".toml", ".txt", ".md", ".rb", ".pl"}
REF_SCAN_EXT = {".md", ".yml", ".yaml", ".json", ".toml"}


class Finding(object):
    __slots__ = ("rule", "level", "path", "line", "msg")

    def __init__(self, rule, level, path, line, msg):
        self.rule, self.level, self.path, self.line, self.msg = rule, level, path, line, msg

    def as_dict(self):
        return {"rule": self.rule, "level": self.level, "file": self.path,
                "line": self.line, "message": self.msg}


# ---------------------------------------------------------------- YAML subset
class FrontmatterError(Exception):
    def __init__(self, msg, line=None):
        Exception.__init__(self, msg)
        self.msg, self.line = msg, line


_KEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.\-]*)\s*:(?:\s+(.*)|\s*)$")


def _indent(s):
    return len(s) - len(s.lstrip(" "))


def _strip_comment(s):
    m = re.search(r"\s#", s)
    return s[:m.start()].rstrip() if m else s


def _scalar(text):
    t = text.strip()
    if t == "" or t in ("~",) or t.lower() == "null":
        return None
    if t.lower() == "true":
        return True
    if t.lower() == "false":
        return False
    if re.match(r"^[-+]?\d+$", t):
        return int(t)
    if re.match(r"^[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?$", t):
        return float(t)
    return t


_DQ_ESC = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/",
           "0": "\0", " ": " "}


def _scan_quoted(s, quote):
    """Return (value, rest_after_close) or None when unterminated."""
    out, i = [], 1
    while i < len(s):
        c = s[i]
        if quote == '"' and c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n == "u" and re.match(r"[0-9a-fA-F]{4}", s[i + 2:i + 6]):
                out.append(chr(int(s[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append(_DQ_ESC.get(n, "\\" + n))
            i += 2
            continue
        if quote == "'" and c == "'" and s[i + 1:i + 2] == "'":
            out.append("'")
            i += 2
            continue
        if c == quote:
            return "".join(out), s[i + 1:]
        out.append(c)
        i += 1
    return None


def _parse_quoted(rest, block, lineno):
    quote = rest[0]
    text, extra = rest, [b.strip() for b in block]
    while True:
        res = _scan_quoted(text, quote)
        if res is not None:
            val, tail = res
            tail = tail.strip()
            if tail and not tail.startswith("#"):
                raise FrontmatterError("unexpected text after closing quote", lineno)
            return val
        if not extra:
            raise FrontmatterError("unterminated quoted string", lineno)
        nxt = extra.pop(0)
        text = text + (" " + nxt if nxt else "\n")


def _dedent(lines):
    nonblank = [l for l in lines if l.strip()]
    if not nonblank:
        return [""] * len(lines)
    k = min(_indent(l) for l in nonblank)
    return [l[k:] if l.strip() else "" for l in lines]


def _block_scalar(header, block, lineno):
    m = re.match(r"^([>|])([+-]?)(\d?)$", header)
    if not m:
        raise FrontmatterError("bad block scalar header", lineno)
    style, chomp = m.group(1), m.group(2)
    lines = _dedent(block)
    while lines and lines[-1] == "":
        lines.pop()
    if style == "|":
        body = "\n".join(lines)
    else:
        groups, cur = [], []
        for l in lines:
            if l == "":
                if cur:
                    groups.append(" ".join(cur))
                    cur = []
                else:
                    groups.append("")
            else:
                cur.append(l.strip())
        if cur:
            groups.append(" ".join(cur))
        body = "\n".join(groups)
    if chomp != "-" and body:
        body += "\n"
    return body


def _parse_value(rest, block, lineno):
    while block and not block[-1].strip():
        block = block[:-1]
    if rest == "":
        nonblank = [l for l in block if l.strip() and not l.lstrip().startswith("#")]
        if not nonblank:
            return None
        first = nonblank[0].lstrip()
        if first.startswith("- ") or first == "-":
            items = []
            for l in nonblank:
                s = l.strip()
                if not (s.startswith("- ") or s == "-"):
                    raise FrontmatterError("mixed list and mapping", lineno)
                items.append(_scalar(_strip_comment(s[1:].strip())))
            return items
        data, _ = parse_yaml_subset(_dedent(block), lineno + 1)
        return data
    if rest[0] in ">|":
        return _block_scalar(rest, block, lineno)
    if rest[0] in "\"'":
        return _parse_quoted(rest, block, lineno)
    if rest[0] in "@`!&*":
        raise FrontmatterError("value starts with reserved indicator '%s' (quote it)" % rest[0], lineno)
    if rest[0] == "[":
        try:
            return json.loads(rest)
        except ValueError:
            inner = rest.strip()
            if not inner.endswith("]"):
                raise FrontmatterError("unterminated flow sequence", lineno)
            return [_scalar(p.strip().strip("'\"")) for p in inner[1:-1].split(",") if p.strip()]
    if rest[0] == "{":
        raise FrontmatterError("flow mappings are not supported by the built-in parser", lineno)
    parts = [_strip_comment(rest)] + [_strip_comment(l.strip()) for l in block
                                      if l.strip() and not l.lstrip().startswith("#")]
    text = " ".join(parts)
    if ": " in text or text.endswith(":"):
        raise FrontmatterError("plain value contains ': ' (quote the value)", lineno)
    return _scalar(text) if len(parts) == 1 else text


def parse_yaml_subset(lines, base_line):
    """Parse a mapping from `lines`; base_line is the file line of lines[0]."""
    data, key_lines = {}, {}
    i, n = 0, len(lines)
    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        lead = raw[:len(raw) - len(raw.lstrip())]
        if "\t" in lead:
            raise FrontmatterError("tab indentation", base_line + i)
        if _indent(raw) != 0:
            raise FrontmatterError("unexpected indentation", base_line + i)
        m = _KEY_RE.match(raw.rstrip())
        if not m:
            raise FrontmatterError("expected 'key: value'", base_line + i)
        key, rest = m.group(1), (m.group(2) or "").strip()
        key_lines[key] = base_line + i
        i += 1
        j = i
        while j < n and (not lines[j].strip() or _indent(lines[j]) > 0):
            j += 1
        data[key] = _parse_value(rest, lines[i:j], base_line + i - 1)
        i = j
    return data, key_lines


def split_frontmatter(text):
    """Return (fm_lines, body_start_line_1based, body_lines, error)."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 1, lines, "file does not start with a '---' frontmatter fence"
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return lines[1:i], i + 2, lines[i + 1:], None
    return None, 1, lines, "closing '---' fence not found"


def load_frontmatter(fm_lines, use_yaml=True):
    """Return (dict, key_lines, error_msg, error_line). Line numbers are file lines."""
    key_lines = {}
    for idx, l in enumerate(fm_lines):
        m = re.match(r"^([A-Za-z0-9_][A-Za-z0-9_.\-]*)\s*:", l)
        if m and m.group(1) not in key_lines:
            key_lines[m.group(1)] = idx + 2
    if use_yaml and _yaml is not None:
        try:
            data = _yaml.safe_load("\n".join(fm_lines))
        except _yaml.YAMLError as e:  # type: ignore[attr-defined]
            mark = getattr(e, "problem_mark", None)
            line = (mark.line + 2) if mark is not None else 2
            problem = getattr(e, "problem", None) or "invalid YAML"
            return None, key_lines, "invalid YAML: %s" % problem, line
        if data is None:
            data = {}
        if not isinstance(data, dict):
            return None, key_lines, "frontmatter is not a YAML mapping", 2
        return data, key_lines, None, None
    try:
        data, kl = parse_yaml_subset(fm_lines, 2)
    except FrontmatterError as e:
        return None, key_lines, "invalid frontmatter: %s" % e.msg, e.line or 2
    return data, kl, None, None


# ------------------------------------------------------------------- helpers
def _read(path):
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return None
    if b"\0" in raw:
        return None
    return raw.decode("utf-8", errors="replace")


def _rel(p):
    try:
        r = os.path.relpath(p)
    except ValueError:
        r = p
    return r.replace(os.sep, "/")


def _walk(top):
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORE_DIRS)
        for f in sorted(filenames):
            yield os.path.join(dirpath, f)


def _fence_mask(lines):
    """Return list[bool]: True when the line is inside (or is) a code fence."""
    out, inside, mark = [], False, None
    for l in lines:
        m = FENCE_RE.match(l)
        if m:
            if not inside:
                inside, mark = True, m.group(1)
            elif m.group(1) == mark:
                inside = False
            out.append(True)
        else:
            out.append(inside)
    return out


def find_skills(roots):
    files = []
    for root in roots:
        if os.path.isfile(root):
            root = os.path.dirname(os.path.abspath(root))
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in IGNORE_DIRS)
            if "SKILL.md" in filenames:
                files.append(os.path.abspath(dirpath))
    dirs = sorted(set(files))
    skills, nested = [], defaultdict(list)
    for d in dirs:
        owners = [o for o in dirs if o != d and d.startswith(o + os.sep)]
        if owners:
            nested[min(owners, key=len)].append(d)
        else:
            skills.append(d)
    return skills, nested


def scan_files(sd):
    """Files scanned by L6-L10: SKILL.md, references/**, scripts/**."""
    out = [os.path.join(sd, "SKILL.md")]
    for sub, exts in (("references", REF_SCAN_EXT), ("scripts", None)):
        top = os.path.join(sd, sub)
        if os.path.isdir(top):
            for p in _walk(top):
                ext = os.path.splitext(p)[1].lower()
                if (exts is None and ext in TEXT_SCRIPT_EXT) or (exts is not None and ext in exts):
                    out.append(p)
    return [p for p in out if os.path.isfile(p)]


def _ver_tuple(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except ValueError:
        return None


# ------------------------------------------------------------------ the checks
def lint_skill(sd, nested_dirs, opts):
    F = []
    skill_md = os.path.join(sd, "SKILL.md")
    P = _rel(skill_md)
    folder = os.path.basename(sd)

    def add(rule, level, path, line, msg):
        F.append(Finding(rule, level, path, line, msg))

    text = _read(skill_md)
    if text is None:
        add("L1", "FAIL", P, 1, "SKILL.md is unreadable or binary")
        return F
    fm_lines, body_start, body_lines, ferr = split_frontmatter(text)
    data, key_lines = None, {}
    if ferr:
        add("L1", "FAIL", P, 1, ferr)
    else:
        data, key_lines, err, eline = load_frontmatter(fm_lines, opts.get("use_yaml", True))
        if err:
            add("L1", "FAIL", P, eline or 2, err)
            data = None
    kl = lambda k: key_lines.get(k, 2)  # noqa: E731

    if data is not None:
        for k in data:
            if k == "metadata":
                add("L1", "WARN", P, kl(k), "'metadata' is reserved and not allowed yet (frontmatter is name, description, version)")
            elif k.lower() in VENDOR_KEYS:
                add("L1", "WARN", P, kl(k), "vendor-specific frontmatter key '%s' does not belong in the canonical copy" % k)
            elif k not in ALLOWED_KEYS:
                add("L1", "WARN", P, kl(k), "unknown frontmatter key '%s'" % k)
        # L2 name
        name = data.get("name")
        if name is None or name == "":
            add("L2", "FAIL", P, kl("name"), "'name' is missing")
        elif not isinstance(name, str):
            add("L2", "FAIL", P, kl("name"), "'name' must be a string")
        else:
            if not NAME_RE.match(name) or len(name) > 64:
                add("L2", "FAIL", P, kl("name"), "name '%s' must be lowercase letters/digits/single hyphens, at most 64 chars" % name)
            if name != folder:
                add("L2", "FAIL", P, kl("name"), "name '%s' does not match folder '%s'" % (name, folder))
        # L3 / L4 / L5 description
        desc = data.get("description")
        if desc is None or (isinstance(desc, str) and not desc.strip()):
            add("L3", "FAIL", P, kl("description"), "'description' is missing or empty")
        elif not isinstance(desc, str):
            add("L3", "FAIL", P, kl("description"), "'description' must be a string")
        else:
            d = " ".join(desc.split())
            if len(d) > DESC_FAIL:
                add("L3", "FAIL", P, kl("description"), "description is %d chars (limit %d)" % (len(d), DESC_FAIL))
            elif len(d) > DESC_WARN:
                add("L3", "WARN", P, kl("description"), "description is %d chars (target under %d)" % (len(d), DESC_WARN))
            if not TRIGGER_RE.search(d):
                add("L4", "FAIL", P, kl("description"), "description has no 'Use when' / 'Use whenever' triggers")
            if ANGLE_RE.search(d):
                add("L5", "WARN", P, kl("description"), "description contains angle brackets (some loaders reject tags)")
            if FIRST_PERSON_RE.search(d):
                add("L5", "WARN", P, kl("description"), "description uses first/second person (I, my, you)")
        # L16 version
        if "version" not in data or data.get("version") in (None, ""):
            add("L16", "FAIL" if opts.get("strict_version") else "WARN", P, 2,
                "'version' is missing" + ("" if opts.get("strict_version") else " (WARN until migration is complete)"))
        elif not SEMVER_RE.match(str(data["version"])) or isinstance(data["version"], float):
            add("L16", "FAIL", P, kl("version"), "version '%s' is not MAJOR.MINOR.PATCH" % data["version"])

    # L13 sizes
    body_text = "\n".join(body_lines)
    nlines, nbytes = len(body_lines), len(body_text.encode("utf-8"))
    if nlines > BODY_FAIL_LINES or nbytes > BODY_FAIL_BYTES:
        add("L13", "FAIL", P, body_start, "SKILL.md body is %d lines / %.1f KB (limit %d lines / %d KB)" % (
            nlines, nbytes / 1024.0, BODY_FAIL_LINES, BODY_FAIL_BYTES // 1024))
    elif nlines > BODY_WARN_LINES or nbytes > BODY_WARN_BYTES:
        add("L13", "WARN", P, body_start, "SKILL.md body is %d lines / %.1f KB (warn above %d lines / %d KB, target %d lines)" % (
            nlines, nbytes / 1024.0, BODY_WARN_LINES, BODY_WARN_BYTES // 1024, BODY_TARGET_LINES))
    ref_dir = os.path.join(sd, "references")
    if os.path.isdir(ref_dir):
        for p in _walk(ref_dir):
            if p.lower().endswith(".md"):
                t = _read(p)
                if t is not None and t.count("\n") + 1 > REF_FAIL_LINES:
                    add("L13", "FAIL", _rel(p), 1, "reference file has %d lines (limit %d)" % (t.count("\n") + 1, REF_FAIL_LINES))
    total = 0
    for p in _walk(sd):
        if os.path.relpath(p, sd).replace(os.sep, "/").startswith("assets/"):
            continue
        try:
            total += os.path.getsize(p)
        except OSError:
            pass
    if total > FOLDER_FAIL:
        add("L13", "FAIL", P, 1, "skill folder is %.0f KB excluding assets (limit %d KB)" % (total / 1024.0, FOLDER_FAIL // 1024))
    elif total > FOLDER_WARN:
        add("L13", "WARN", P, 1, "skill folder is %.0f KB excluding assets (target under %d KB)" % (total / 1024.0, FOLDER_WARN // 1024))

    # L6-L10 content scans
    for p in scan_files(sd):
        t = _read(p)
        if t is None:
            continue
        rp = _rel(p)
        for ln, line in enumerate(t.splitlines(), 1):
            m6 = sorted({m.group(0) for m in L6_RE.finditer(line)})
            if m6:
                add("L6", "FAIL", rp, ln, "vendor tool-call name: %s" % ", ".join(m6))
            m7 = sorted({m.group(0).strip() for r in L7_RES for m in r.finditer(line)})
            if m7:
                add("L7", "FAIL", rp, ln, "model name or tier: %s" % ", ".join(m7))
            m8 = sorted({m.group(1) for m in L8_RE.finditer(line)})
            if m8:
                add("L8", "FAIL", rp, ln, "host product named as actor: %s" % ", ".join(m8))
            if any(r.search(line) for r in L9_RES):
                add("L9", "FAIL", rp, ln, "absolute machine path")
            kinds = []
            for kind, r in L10_RES:
                for m in r.finditer(line):
                    if not PLACEHOLDER_RE.search(m.group(0)):
                        kinds.append(kind)
                        break
            if kinds:
                add("L10", "FAIL", rp, ln, "possible secret (%s); value not shown" % ", ".join(kinds))

    # L11 forbidden files
    for dirpath, dirnames, filenames in os.walk(sd):
        for d in list(dirnames):
            if d in ("node_modules", "__pycache__"):
                add("L11", "FAIL", _rel(os.path.join(dirpath, d)), 1, "forbidden directory '%s' inside a skill" % d)
            if d in IGNORE_DIRS:
                dirnames.remove(d)
        dirnames.sort()
        for f in sorted(filenames):
            fl = f.lower()
            p = os.path.join(dirpath, f)
            bad = None
            if fl == ".env" or (fl.startswith(".env.") and fl != ".env.example"):
                bad = "env file"
            elif fl.endswith((".pem", ".key")):
                bad = "key file"
            elif fl.endswith(".log"):
                bad = "log file"
            elif fl == "config.json":
                t = _read(p) or ""
                if re.search(r"(?i)\"[^\"]*(key|token|secret|password)[^\"]*\"\s*:\s*\"[^\"]{8,}\"", t):
                    bad = "config.json with key-like fields"
            if bad:
                add("L11", "FAIL", _rel(p), 1, "forbidden file (%s)" % bad)

    # L12 links and orphans
    md_files = [p for p in _walk(sd) if p.lower().endswith(".md")]
    for p in md_files:
        t = _read(p)
        if t is None:
            continue
        lines = t.splitlines()
        mask = _fence_mask(lines)
        for ln, line in enumerate(lines, 1):
            if mask[ln - 1]:
                continue
            targets = []
            for m in LINK_RE.finditer(line):
                tg = m.group(1)
                if re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|#)", tg):
                    continue
                targets.append(tg.split("#")[0].split("?")[0])
            for m in TICK_PATH_RE.finditer(line):
                targets.append(m.group(1).rstrip(".,;:)"))
            for tg in targets:
                if not tg or re.search(r"[<>*{}$|]|\.\.\.", tg):
                    continue
                tg = tg.replace("%20", " ")
                cands = [os.path.join(os.path.dirname(p), tg)]
                if tg.startswith(("scripts/", "references/", "assets/", "./scripts/", "./references/", "./assets/")):
                    cands.append(os.path.join(sd, tg))
                if not any(os.path.exists(c) for c in cands):
                    add("L12", "FAIL", _rel(p), ln, "broken relative link or path: %s" % tg)
    orphans = []
    for sub in ("references", "scripts"):
        top = os.path.join(sd, sub)
        if not os.path.isdir(top):
            continue
        for p in _walk(top):
            rel = os.path.relpath(p, sd).replace(os.sep, "/")
            parts = rel.split("/")
            hit = rel in text or parts[-1] in text
            for k in range(2, len(parts)):
                if "/".join(parts[:k]) in text:
                    hit = True
            if not hit:
                orphans.append(rel)
    if orphans:
        add("L12", "WARN", P, 1, "%d file(s) in references/ or scripts/ not mentioned in SKILL.md (first: %s)" % (
            len(orphans), ", ".join(orphans[:3])))

    # L14 nested SKILL.md
    for nd in nested_dirs:
        add("L14", "FAIL", _rel(os.path.join(nd, "SKILL.md")), 1,
            "nested SKILL.md below skill '%s' (rename sub-guides to references/<topic>.md)" % folder)

    # L17 style
    lines = body_lines
    mask = _fence_mask(lines)
    heads = []
    for i, l in enumerate(lines):
        if mask[i]:
            continue
        m = HEADING_RE.match(l)
        if m:
            heads.append((body_start + i, len(m.group(1)), m.group(2)))
            if EMOJI_RE.search(m.group(2)):
                add("L17", "WARN", P, body_start + i, "emoji in heading")
    low = [h[2].lower() for h in heads]
    missing = []
    if not any(h[1] == 1 for h in heads):
        missing.append("# Title")
    for label, keys in (("When to use", ("when to use",)), ("Requirements", ("requirements",)),
                        ("Workflow or Rules", ("workflow", "rules")), ("Read next", ("read next",))):
        if not any(any(k in t for k in keys) for t in low):
            missing.append("## " + label)
    if not any("changelog" in t for t in low) and not os.path.exists(os.path.join(sd, "CHANGELOG.md")):
        missing.append("Changelog")
    if missing:
        add("L17", "WARN", P, 1, "missing recommended sections: %s" % ", ".join(missing))

    # L18 script hygiene
    sdir = os.path.join(sd, "scripts")
    if os.path.isdir(sdir):
        names = {os.path.splitext(f)[0] for f in os.listdir(sdir)}
        for p in _walk(sdir):
            ext = os.path.splitext(p)[1].lower()
            t = _read(p)
            if t is None:
                continue
            rp = _rel(p)
            if ext in (".py", ".sh", ".js", ".mjs"):
                if not t.startswith("#!"):
                    add("L18", "WARN", rp, 1, "script has no shebang")
                if not re.search(r"--help|argparse|optparse|\bclick\b|\btyper\b|commander|yargs", t):
                    add("L18", "WARN", rp, 1, "script has no --help handling")
            for ln, line in enumerate(t.splitlines(), 1):
                if re.search(r"python[\d.]*\.exe|/usr/bin/python\d?\b|C:[\\/]Python", line, re.I):
                    add("L18", "WARN", rp, ln, "hardcoded interpreter path")
            if ext in (".ps1", ".sh"):
                stem = os.path.splitext(os.path.basename(p))[0]
                others = [f for f in os.listdir(sdir) if os.path.splitext(f)[0] == stem and
                          os.path.splitext(f)[1].lower() != ext]
                if not others and not any(os.path.splitext(f)[1].lower() in (".py", ".js", ".mjs") for f in os.listdir(sdir)):
                    add("L18", "WARN", rp, 1, "%s script has no cross-platform counterpart" % ext)
    # L16 version bump against a base ref
    base = opts.get("base")
    if base and data is not None:
        F.extend(check_version_bump(sd, data, base, P))
    return F


def _git(cwd, *args):
    r = subprocess.run(["git", "-C", cwd] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True)
    return r.returncode, r.stdout, r.stderr


def check_version_bump(sd, data, base, P):
    rc, top, err = _git(sd, "rev-parse", "--show-toplevel")
    if rc != 0:
        return []
    top = top.strip()
    rc, mb, _ = _git(top, "merge-base", base, "HEAD")
    ref = mb.strip() if rc == 0 and mb.strip() else base
    rel = os.path.relpath(os.path.realpath(sd), os.path.realpath(top)).replace(os.sep, "/")
    rc, out, err = _git(top, "diff", "--name-only", ref, "--", rel)
    if rc != 0:
        raise RuntimeError("git diff against '%s' failed: %s" % (base, err.strip()))
    if not out.strip():
        return []
    rc, old, _ = _git(top, "show", "%s:%s/SKILL.md" % (ref, rel))
    if rc != 0:
        return []  # new skill in this change
    fl, _, _, ferr = split_frontmatter(old)
    old_v = None
    if not ferr:
        od, _, oerr, _ = load_frontmatter(fl)
        if od and not oerr:
            old_v = od.get("version")
    new_v = data.get("version")
    if new_v in (None, ""):
        return [Finding("L16", "FAIL", P, 2, "skill files changed vs %s but 'version' is missing" % base)]
    if old_v in (None, ""):
        return []
    a, b = _ver_tuple(new_v), _ver_tuple(old_v)
    if a is None or b is None or a <= b:
        return [Finding("L16", "FAIL", P, 2, "skill files changed vs %s but version %s was not increased (was %s)" % (base, new_v, old_v))]
    return []


def lint_all(roots, opts):
    skills, nested = find_skills(roots)
    results, names = [], defaultdict(list)
    for sd in skills:
        f = lint_skill(sd, sorted(nested.get(sd, [])), opts)
        results.append([sd, f])
        t = _read(os.path.join(sd, "SKILL.md")) or ""
        fl, _, _, ferr = split_frontmatter(t)
        nm = os.path.basename(sd)
        if not ferr:
            d, _, e, _ = load_frontmatter(fl, opts.get("use_yaml", True))
            if d and isinstance(d.get("name"), str):
                nm = d["name"]
        names[nm.lower()].append(sd)
    for nm, dirs in names.items():
        if len(dirs) > 1:
            for sd in dirs:
                for r in results:
                    if r[0] == sd:
                        r[1].append(Finding("L15", "WARN", _rel(os.path.join(sd, "SKILL.md")), 2,
                                            "duplicate skill name '%s' also in: %s" % (
                                                nm, ", ".join(_rel(x) for x in dirs if x != sd))))
    known = {os.path.basename(sd) for sd in skills}
    for sd, fl in results:
        root = next((r for r in map(os.path.abspath, roots)
                     if os.path.isdir(r) and sd.startswith(r + os.sep)), None)
        fl.extend(check_skill_refs(sd, known, root or os.path.abspath(roots[0])))
    for r in results:
        r[1].sort(key=lambda x: (x.path, x.line, x.rule))
    return results


def _plugin_name(root):
    """Return (name, error) from <root>/.claude-plugin/plugin.json."""
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    if not os.path.isfile(path):
        return None, None
    try:
        with open(path, encoding="utf-8") as fh:
            name = json.load(fh).get("name")
    except (OSError, ValueError, AttributeError) as e:
        return None, "cannot read .claude-plugin/plugin.json: %s" % e
    return name, None


def check_skill_refs(sd, known, root):
    """L19: skills named next to the word 'skill' must exist in this lint run."""
    F = []
    plugin, perr = _plugin_name(root)
    reported_perr = False
    top = os.path.join(sd, "references")
    files = [os.path.join(sd, "SKILL.md")] + (
        [p for p in _walk(top) if p.lower().endswith(".md")] if os.path.isdir(top) else [])
    for p in files:
        t = _read(p)
        if t is None:
            continue
        lines = t.splitlines()
        mask = _fence_mask(lines)
        for ln, line in enumerate(lines, 1):
            if mask[ln - 1]:
                continue
            for r in L19_RES:
                for m in r.finditer(line):
                    prefix, name = m.group(1), m.group(2)
                    if name not in known:
                        F.append(Finding("L19", "FAIL", _rel(p), ln,
                                         "referenced skill '%s' does not exist" % name))
                    elif prefix and perr:
                        if not reported_perr:
                            F.append(Finding("L19", "FAIL", _rel(p), ln, perr))
                            reported_perr = True
                    elif prefix and plugin is None:
                        F.append(Finding("L19", "FAIL", _rel(p), ln,
                                         "prefix '%s' but no .claude-plugin/plugin.json" % prefix))
                    elif prefix and prefix != plugin:
                        F.append(Finding("L19", "FAIL", _rel(p), ln,
                                         "prefix '%s' does not match plugin name '%s'" % (prefix, plugin)))
    return F


def status_of(findings):
    if any(f.level == "FAIL" for f in findings):
        return "FAIL"
    return "WARN" if findings else "PASS"


# -------------------------------------------------------------------- output
def _esc_prop(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C")


def _esc_msg(s):
    return str(s).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def summarize(results):
    per_rule = Counter()
    counts = Counter()
    for sd, f in results:
        counts[status_of(f)] += 1
        for x in f:
            per_rule[(x.rule, x.level)] += 1
    return counts, per_rule


def render(results, fmt, summary_only=False):
    counts, per_rule = summarize(results)
    out = []
    if fmt == "json":
        doc = {"skills": [{"skill": os.path.basename(sd), "path": _rel(sd), "status": status_of(f),
                           "findings": [x.as_dict() for x in f]} for sd, f in results],
               "totals": dict(counts),
               "by_rule": {"%s %s" % (r, l): n for (r, l), n in sorted(per_rule.items(), key=lambda kv: (int(kv[0][0][1:]), kv[0][1]))}}
        return json.dumps(doc, indent=2)
    for sd, f in results:
        st = status_of(f)
        if fmt == "github":
            for x in f:
                kind = "error" if x.level == "FAIL" else "warning"
                out.append("::%s file=%s,line=%d,title=%s::%s" % (kind, _esc_prop(x.path), x.line, x.rule, _esc_msg(x.msg)))
        out.append("%-5s %s" % (st, os.path.basename(sd)))
        if fmt == "text" and not summary_only:
            for x in sorted(f, key=lambda y: (y.level != "FAIL", y.path, y.line)):
                out.append("    %-4s %-3s %s:%d  %s" % (x.level, x.rule, x.path, x.line, x.msg))
    out.append("")
    out.append("Skills: %d  PASS %d  WARN %d  FAIL %d" % (len(results), counts["PASS"], counts["WARN"], counts["FAIL"]))
    if per_rule:
        out.append("By rule: " + ", ".join("%s %s x%d" % (r, l, n) for (r, l), n in
                                            sorted(per_rule.items(), key=lambda kv: (int(kv[0][0][1:]), kv[0][1]))))
    return "\n".join(out)


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Lint SKILL.md skills (checks L1-L19).")
    ap.add_argument("paths", nargs="*", help="directories to scan (default: repo root)")
    ap.add_argument("--format", choices=["text", "github", "json"], default="text")
    ap.add_argument("--base", help="git ref to compare versions against (L16 bump check)")
    ap.add_argument("--strict-version", action="store_true", help="missing version is FAIL")
    ap.add_argument("--no-yaml", action="store_true", help="force the built-in frontmatter parser")
    ap.add_argument("--summary-only", action="store_true", help="omit per-finding lines in text format")
    a = ap.parse_args(argv)
    roots = a.paths or [os.path.dirname(here)]
    for r in roots:
        if not os.path.exists(r):
            sys.stderr.write("error: path not found: %s\n" % r)
            return 2
    opts = {"use_yaml": not a.no_yaml, "strict_version": a.strict_version, "base": a.base}
    try:
        results = lint_all(roots, opts)
    except RuntimeError as e:
        sys.stderr.write("error: %s\n" % e)
        return 2
    if not results:
        sys.stderr.write("error: no SKILL.md found under: %s\n" % ", ".join(roots))
        return 2
    sys.stdout.write(render(results, a.format, a.summary_only) + "\n")
    return 1 if any(status_of(f) == "FAIL" for _, f in results) else 0


if __name__ == "__main__":
    sys.exit(main())
