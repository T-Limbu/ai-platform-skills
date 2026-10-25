"""Tests for scripts/lint_skills.py. Run: python -m unittest discover -s tests -v
(or `pytest tests`). Fixtures are built in temp dirs; secret-looking values are
assembled at runtime so no literal credential exists in this file."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import lint_skills as L  # noqa: E402

GOOD_DESC = "Use when linting fixtures in tests. Checks one thing."
GOOD_BODY = """# Fixture

## When to use
- always

## Requirements
- none

## Workflow
1. do it

## Read next
none

## Changelog
- 1.0.0: init
"""


def make_skill(root, name="demo", fm=None, body=GOOD_BODY, files=None, raw=None):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    if raw is None:
        if fm is None:
            fm = "name: %s\ndescription: %s\nversion: 1.0.0" % (name, GOOD_DESC)
        raw = "---\n%s\n---\n\n%s" % (fm, body)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(raw)
    for rel, content in (files or {}).items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
    return d


def run_lint(root, **opts):
    return dict((os.path.basename(sd), f) for sd, f in L.lint_all([root], opts))


def fired(findings, rule, level=None):
    return [f for f in findings if f.rule == rule and (level is None or f.level == level)]


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.root = self._t.name

    def tearDown(self):
        self._t.cleanup()

    def reset(self):
        """Fresh empty temp dir mid-test."""
        self._t.cleanup()
        self.setUp()

    def lint(self, name="demo", **opts):
        return run_lint(self.root, **opts)[name]


class CleanSkill(Base):
    def test_clean_skill_passes(self):
        make_skill(self.root)
        f = self.lint()
        self.assertEqual(L.status_of(f), "PASS", [x.as_dict() for x in f])


class FrontmatterChecks(Base):
    def test_L1_missing_frontmatter(self):
        make_skill(self.root, raw="# no frontmatter\n")
        self.assertTrue(fired(self.lint(), "L1", "FAIL"))

    def test_L1_unclosed(self):
        make_skill(self.root, raw="---\nname: demo\n")
        self.assertTrue(fired(self.lint(), "L1", "FAIL"))

    def test_L1_bad_yaml_both_parsers(self):
        for use_yaml in (True, False):
            self.reset()
            make_skill(self.root, fm="name: demo\ndescription: Use when a: b: c\n  oops: [")
            self.assertTrue(fired(self.lint(use_yaml=use_yaml), "L1", "FAIL"), use_yaml)

    def test_L1_metadata_reserved_warn(self):
        make_skill(self.root, fm="name: demo\ndescription: %s\nversion: 1.0.0\nmetadata:\n  owner: me" % GOOD_DESC)
        f = self.lint()
        self.assertTrue(fired(f, "L1", "WARN"))
        self.assertFalse(fired(f, "L1", "FAIL"))

    def test_L1_vendor_key_warn(self):
        make_skill(self.root, fm="name: demo\ndescription: %s\nversion: 1.0.0\nallowed-tools: x" % GOOD_DESC)
        self.assertTrue(fired(self.lint(), "L1", "WARN"))

    def test_L2_name_mismatch_and_pattern(self):
        make_skill(self.root, fm="name: other\ndescription: %s\nversion: 1.0.0" % GOOD_DESC)
        self.assertTrue(fired(self.lint(), "L2", "FAIL"))
        make_skill(self.root, name="Bad_Name", fm="name: Bad_Name\ndescription: %s\nversion: 1.0.0" % GOOD_DESC)
        self.assertTrue(fired(self.lint("Bad_Name"), "L2", "FAIL"))

    def test_L2_missing_name(self):
        make_skill(self.root, fm="description: %s\nversion: 1.0.0" % GOOD_DESC)
        self.assertTrue(fired(self.lint(), "L2", "FAIL"))

    def test_L3_missing_and_too_long_and_warn(self):
        make_skill(self.root, fm="name: demo\nversion: 1.0.0")
        self.assertTrue(fired(self.lint(), "L3", "FAIL"))
        make_skill(self.root, fm='name: demo\nversion: 1.0.0\ndescription: "Use when %s"' % ("x" * 1100))
        self.assertTrue(fired(self.lint(), "L3", "FAIL"))
        make_skill(self.root, fm='name: demo\nversion: 1.0.0\ndescription: "Use when %s"' % ("x" * 600))
        f = self.lint()
        self.assertTrue(fired(f, "L3", "WARN"))
        self.assertFalse(fired(f, "L3", "FAIL"))

    def test_L4_no_triggers(self):
        make_skill(self.root, fm="name: demo\nversion: 1.0.0\ndescription: Does things with files.")
        self.assertTrue(fired(self.lint(), "L4", "FAIL"))

    def test_L5_angle_and_first_person(self):
        make_skill(self.root, fm='name: demo\nversion: 1.0.0\ndescription: "Use when <thing> happens and you want help."')
        w = fired(self.lint(), "L5", "WARN")
        self.assertEqual(len(w), 2)

    def test_L16_version_missing_warn_then_strict_fail(self):
        make_skill(self.root, fm="name: demo\ndescription: %s" % GOOD_DESC)
        self.assertTrue(fired(self.lint(), "L16", "WARN"))
        self.assertTrue(fired(self.lint(strict_version=True), "L16", "FAIL"))

    def test_L16_version_malformed(self):
        make_skill(self.root, fm="name: demo\ndescription: %s\nversion: 1.0" % GOOD_DESC)
        self.assertTrue(fired(self.lint(), "L16", "FAIL"))


class ContentChecks(Base):
    def body_with(self, line):
        return GOOD_BODY + "\n" + line + "\n"

    def test_L6_tool_call_names(self):
        make_skill(self.root, body=self.body_with("Call run_shell_command then WebFetch."))
        f = fired(self.lint(), "L6", "FAIL")
        self.assertEqual(len(f), 1)

    def test_L7_models_and_tiers(self):
        for line in ("Use Gemini Flash here.", "Escalate to `pro` for hard work.", 'cfg {"Model": "x"}', "ask Claude Sonnet"):
            self.reset()
            make_skill(self.root, body=self.body_with(line))
            self.assertTrue(fired(self.lint(), "L7", "FAIL"), line)

    def test_L7_bare_pro_not_flagged(self):
        make_skill(self.root, body=self.body_with("Use SF Pro and the Pro Heading rule."))
        self.assertFalse(fired(self.lint(), "L7"))

    def test_L8_host_product(self):
        make_skill(self.root, body=self.body_with("This skill equips Antigravity with tools."))
        self.assertTrue(fired(self.lint(), "L8", "FAIL"))

    def test_L8_css_cursor_not_flagged(self):
        make_skill(self.root, body=self.body_with("Set cursor: pointer and move the cursor."))
        self.assertFalse(fired(self.lint(), "L8"))

    def test_L9_machine_paths(self):
        for line in ("Open C:\\Users\\someone\\Desktop\\x", "see /home/someone/project/x", "\\\\server\\share$\\x"):
            self.reset()
            make_skill(self.root, body=self.body_with(line))
            self.assertTrue(fired(self.lint(), "L9", "FAIL"), line)

    def test_L10_secrets_fire_and_are_never_printed(self):
        secrets = {
            "GitHub token": "ghp_" + "aB3dE5gH7jK9mN1pQ3sT5vX7zA9cE1gI3kM5",
            "Google API key": "AIza" + "SyA1B2C3D4E5F6G7H8I9J0KlMnOpQrStUvW"[:35],
            "sk- style API key": "sk-" + "proj_AbCdEfGhIjKlMnOpQrStUvWx",
            "AWS access key id": "AKIA" + "ABCDEFGHIJKLMNOP",
            "private key block": "-----BEGIN " + "RSA PRIVATE KEY-----",
            "credential assignment": 'api_key = "' + "Zq8Lw3Rt6Yu9Io2P" + '"',
        }
        for kind, val in secrets.items():
            self.reset()
            make_skill(self.root, body=self.body_with("token: " + val if kind != "credential assignment" else val))
            f = fired(self.lint(), "L10", "FAIL")
            self.assertTrue(f, kind)
            blob = " ".join(x.msg for x in f)
            self.assertNotIn(val[8:20], blob)
            out = L.render([(os.path.join(self.root, "demo"), self.lint())], "text")
            self.assertNotIn(val[8:20], out)

    def test_L10_placeholder_ok(self):
        make_skill(self.root, body=self.body_with("export TOKEN=ghp_" + "x" * 36))
        self.assertFalse(fired(self.lint(), "L10"))

    def test_L10_scans_references_and_scripts(self):
        make_skill(self.root, files={"scripts/run.py": "KEY = 'AKIA" + "ABCDEFGHIJKLMNOP'\n"})
        f = fired(self.lint(), "L10", "FAIL")
        self.assertTrue(f and f[0].path.endswith("scripts/run.py"))

    def test_L11_forbidden_files(self):
        make_skill(self.root, files={".env": "A=1\n", ".env.example": "A=\n", "x.pem": "k", "a.log": "l",
                                     "node_modules/p/i.js": "1", "config.json": '{"api_key": "abcdefghijkl"}'})
        paths = sorted(os.path.basename(x.path) for x in fired(self.lint(), "L11", "FAIL"))
        self.assertEqual(paths, [".env", "a.log", "config.json", "node_modules", "x.pem"])

    def test_L12_broken_links(self):
        make_skill(self.root, body=self.body_with("See [x](references/missing.md) and `scripts/nope.py`."))
        self.assertEqual(len(fired(self.lint(), "L12", "FAIL")), 2)

    def test_L12_good_links_and_fences_ok(self):
        body = self.body_with("See [x](references/a.md).\n\n```\n[y](nowhere.md)\n```\n")
        make_skill(self.root, body=body, files={"references/a.md": "# a\n"})
        self.assertFalse(fired(self.lint(), "L12", "FAIL"))

    def test_L12_orphan_warn(self):
        make_skill(self.root, files={"references/unused.md": "# u\n"})
        f = fired(self.lint(), "L12", "WARN")
        self.assertTrue(f)

    def test_L13_lengths(self):
        make_skill(self.root, body="# T\n" + "line\n" * 450)
        self.assertTrue(fired(self.lint(), "L13", "FAIL"))
        make_skill(self.root, body="# T\n" + "line\n" * 320)
        f = self.lint()
        self.assertTrue(fired(f, "L13", "WARN"))
        self.assertFalse(fired(f, "L13", "FAIL"))
        make_skill(self.root, body="# T\n" + ("x" * 99 + "\n") * 130)  # about 13 KB, 131 lines
        self.assertTrue(fired(self.lint(), "L13", "FAIL"))
        make_skill(self.root, body="# T\n" + ("x" * 99 + "\n") * 95)  # about 9.5 KB
        f = self.lint()
        self.assertTrue(fired(f, "L13", "WARN") and not fired(f, "L13", "FAIL"))

    def test_L13_reference_too_long(self):
        make_skill(self.root, files={"references/big.md": "x\n" * 1600})
        self.assertTrue(fired(self.lint(), "L13", "FAIL"))

    def test_L14_nested_skill(self):
        make_skill(self.root, files={"references/guides/SKILL.md": "---\nname: g\ndescription: Use when x\n---\n"})
        f = self.lint()
        self.assertTrue(fired(f, "L14", "FAIL"))
        self.assertEqual(len(run_lint(self.root)), 1)

    def test_L15_duplicate_names(self):
        make_skill(self.root, name="aa")
        make_skill(os.path.join(self.root, "sub"), name="bb", fm="name: aa\ndescription: %s\nversion: 1.0.0" % GOOD_DESC)
        res = L.lint_all([self.root], {})
        self.assertTrue(any(fired(f, "L15", "WARN") for _, f in res))

    def test_L17_emoji_and_missing_sections(self):
        make_skill(self.root, body="# \U0001F680 Title\n\ntext\n")
        f = fired(self.lint(), "L17", "WARN")
        self.assertEqual(len(f), 2)  # emoji heading + missing sections
        self.assertFalse(fired(self.lint(), "L17", "FAIL"))

    def test_L18_script_hygiene(self):
        make_skill(self.root, body=GOOD_BODY + "\nUses `scripts/run.py` and scripts/win.ps1.\n",
                   files={"scripts/run.py": "print(1)\nx = 'C:\\\\Python313\\\\python.exe'\n"})
        f = fired(self.lint(), "L18", "WARN")
        msgs = " ".join(x.msg for x in f)
        self.assertIn("shebang", msgs)
        self.assertIn("--help", msgs)
        self.assertIn("interpreter", msgs)


class VersionBump(Base):
    def git(self, *a):
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e.x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e.x")
        subprocess.run(["git", "-C", self.root] + list(a), check=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_L16_bump_required(self):
        self.git("init", "-q")
        d = make_skill(self.root)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.assertFalse(fired(self.lint(base="HEAD"), "L16", "FAIL"))  # unchanged
        with open(os.path.join(d, "SKILL.md"), "a") as fh:
            fh.write("\nmore text\n")
        self.assertTrue(fired(self.lint(base="HEAD"), "L16", "FAIL"))  # changed, same version
        p = os.path.join(d, "SKILL.md")
        with open(p) as fh:
            s = fh.read().replace("version: 1.0.0", "version: 1.0.1")
        with open(p, "w") as fh:
            fh.write(s)
        self.assertFalse(fired(self.lint(base="HEAD"), "L16", "FAIL"))  # bumped


class ParserAndCli(Base):
    def test_folded_and_quoted_scalars_parse(self):
        fm = ('name: demo\ndescription: >\n  Use when folding text\n  across several lines.\n'
              'version: "1.2.3"')
        make_skill(self.root, fm=fm)
        for use_yaml in (True, False):
            f = self.lint(use_yaml=use_yaml)
            self.assertEqual(L.status_of(f), "PASS", (use_yaml, [x.as_dict() for x in f]))

    def test_fallback_parser_values(self):
        data, _ = L.parse_yaml_subset(
            ['name: demo', "description: 'It''s: fine'", 'x: "a \\"b\\" c"', 'f: >-', '  one', '  two', '', '  three',
             'l: |', '  keep', '  lines', 'm:', '  k: v'], 2)
        self.assertEqual(data["description"], "It's: fine")
        self.assertEqual(data["x"], 'a "b" c')
        self.assertEqual(data["f"], "one two\nthree")
        self.assertEqual(data["l"], "keep\nlines\n")
        self.assertEqual(data["m"], {"k": "v"})

    def test_fallback_rejects_unquoted_colon(self):
        with self.assertRaises(L.FrontmatterError):
            L.parse_yaml_subset(["description: Use when a: b"], 2)

    def test_exit_codes_and_formats(self):
        make_skill(self.root, name="good")
        make_skill(self.root, name="bad", fm="name: bad\ndescription: nothing here\nversion: 1.0.0")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = L.main([self.root, "--format", "github"])
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("::error file=", out)
        self.assertIn("title=L4", out)
        self.assertIn("FAIL  bad", out)
        self.assertIn("PASS  good", out)
        # all-pass tree exits 0
        self.reset()
        make_skill(self.root, name="good")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(L.main([self.root]), 0)

    def test_json_format(self):
        make_skill(self.root)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            L.main([self.root, "--format", "json"])
        import json
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["totals"], {"PASS": 1})


if __name__ == "__main__":
    unittest.main()
