"""Tests for project-docs/scripts/check_docs.py. Run: python -m unittest discover -s tests -v
Fixture repos are built in temp dirs; git is used for the stamp checks."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "project-docs", "scripts"))
import check_docs as C  # noqa: E402

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def git(root, *args):
    return subprocess.run(GIT + ["-C", root] + list(args), check=True, capture_output=True, text=True).stdout.strip()


def commit(root, msg="c"):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)
    return git(root, "rev-parse", "HEAD")


def init_repo(root):
    git(root, "init", "-q")
    write(root, "src/app.py", "x = 1\n")
    return commit(root, "init")


def messages(items):
    return [m for _, _, m in items]


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def good_docs(self, sha):
        write(self.root, "docs/INDEX.md", "| Path |\n| -- |\n| `architecture.md` |\n| `PROGRESS.md` |\n")
        write(self.root, "docs/architecture.md",
              "# Architecture\n\nVerified against `%s`, 2026-10-29.\n\nSee `src/app.py` and [runbook](#run).\n" % sha)
        write(self.root, "docs/PROGRESS.md", "# Progress\n\n## 2026-10-29 First\n\n* Goal: g\n* Done: d\n")


class TestClean(Base):
    def test_clean_repo_has_no_findings(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        rep = C.run(self.root)
        self.assertEqual(rep.errors, [])
        self.assertEqual(rep.warnings, [])

    def test_missing_docs_folder_is_error(self):
        rep = C.run(self.root)
        self.assertIn("no docs/ folder", messages(rep.errors))


class TestIndex(Base):
    def test_unlisted_doc_is_error(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/runbook.md", "Verified against `%s`.\n" % sha)
        rep = C.run(self.root)
        self.assertIn(("docs/runbook.md", 1, "not listed in docs/INDEX.md"), rep.errors)

    def test_progress_archive_is_exempt(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/progress/2025.md", "# 2025\n")
        self.assertEqual(C.run(self.root).errors, [])

    def test_missing_index_is_error(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        os.remove(os.path.join(self.root, "docs", "INDEX.md"))
        self.assertIn("docs/INDEX.md is missing", messages(C.run(self.root).errors))


class TestLinks(Base):
    def test_broken_link_is_error_and_others_ignored(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/INDEX.md",
              "`architecture.md` [ok](architecture.md) [web](https://example.com) [gone](missing.md#x)\n"
              "```\n[fenced](nowhere.md)\n```\n`[code](span.md)`\n")
        errs = C.run(self.root).errors
        self.assertEqual([e for e in errs if "broken" in e[2]],
                         [("docs/INDEX.md", 1, "broken relative link: missing.md#x")])


class TestStamps(Base):
    def test_missing_stamp_is_error(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/architecture.md", "# Architecture\n")
        self.assertTrue(any("no verified stamp" in m for m in messages(C.run(self.root).errors)))

    def test_stamp_with_words_before_sha(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/architecture.md",
              "Verified against this repo at `%s`, and against `other` at `c6d1596`, on 2026-10-29.\n" % sha[:7])
        rep = C.run(self.root)
        self.assertEqual(rep.errors, [])
        self.assertEqual(rep.warnings, [])

    def test_bare_verified_is_warning(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/architecture.md", "Last verified 2026-10-29.\n")
        rep = C.run(self.root)
        self.assertEqual(rep.errors, [])
        self.assertTrue(any("has no commit sha" in m for m in messages(rep.warnings)))

    def test_unknown_sha_is_error(self):
        sha = init_repo(self.root)
        self.good_docs("0" * 40)
        self.assertTrue(any("does not exist" in m for m in messages(C.run(self.root).errors)), sha)

    def test_not_a_git_repo_warns(self):
        self.good_docs("abc1234")
        rep = C.run(self.root)
        self.assertEqual(rep.errors, [])
        self.assertTrue(any("cannot check sha" in m for m in messages(rep.warnings)))

    def test_stale_named_files_warn(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        for i in range(3):
            write(self.root, "src/app.py", "x = %d\n" % (i + 2))
            commit(self.root, "edit %d" % i)
        old = C.STALE_COMMITS
        C.STALE_COMMITS = 2
        try:
            rep = C.run(self.root)
        finally:
            C.STALE_COMMITS = old
        self.assertTrue(any("3 commits since" in m for m in messages(rep.warnings)))


class TestProgress(Base):
    def test_too_many_entries_is_error(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        body = "# Progress\n\n" + "".join("## 2026-10-%02d e\n\n* x\n\n" % d for d in range(1, 12))
        write(self.root, "docs/PROGRESS.md", body)
        self.assertTrue(any("11 entries" in m for m in messages(C.run(self.root).errors)))

    def test_long_entry_is_error(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/PROGRESS.md", "# Progress\n\n## 2026-10-29 long\n" + "* line\n" * 11)
        self.assertIn(("docs/PROGRESS.md", 3, "entry has 11 lines (limit 10)"), C.run(self.root).errors)

    def test_ten_by_ten_is_allowed(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        body = "# Progress\n\n" + "".join("## 2026-10-%02d e\n" % d + "* x\n" * 10 for d in range(1, 11))
        write(self.root, "docs/PROGRESS.md", body)
        self.assertEqual(C.run(self.root).errors, [])


class TestCli(Base):
    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = C.main(list(args))
        return code, out.getvalue()

    def test_exit_codes_and_text_sections(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        self.assertEqual(self.run_main(self.root)[0], 0)
        write(self.root, "docs/extra.md", "Last verified.\n")
        code, out = self.run_main(self.root)
        self.assertEqual(code, 1)
        self.assertIn("Errors:", out)
        self.assertIn("Warnings:", out)

    def test_github_format(self):
        sha = init_repo(self.root)
        self.good_docs(sha)
        write(self.root, "docs/extra.md", "Last verified.\n")
        code, out = self.run_main(self.root, "--format", "github")
        self.assertEqual(code, 1)
        self.assertIn("::error file=docs/extra.md,line=1::not listed in docs/INDEX.md", out)
        self.assertIn("::warning file=docs/extra.md,line=1::", out)

    def test_missing_root_is_usage_error(self):
        self.assertEqual(self.run_main(os.path.join(self.root, "nope"))[0], 2)


if __name__ == "__main__":
    unittest.main()
