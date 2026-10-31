"""Tests for the Claude Code plugin manifests (.claude-plugin/). They read the
real repo root; no network, and nothing here invokes the claude CLI."""
import json
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PLUGIN = os.path.join(ROOT, ".claude-plugin", "plugin.json")
MARKET = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class PluginManifest(unittest.TestCase):
    def test_both_files_parse(self):
        self.assertIsInstance(load(PLUGIN), dict)
        self.assertIsInstance(load(MARKET), dict)

    def test_plugin_name_matches_marketplace_entry(self):
        plugin, market = load(PLUGIN), load(MARKET)
        names = [p["name"] for p in market["plugins"]]
        self.assertIn(plugin["name"], names)
        self.assertEqual(len(names), 1)
        self.assertRegex(plugin["name"], NAME_RE)
        self.assertFalse(plugin["name"].startswith(("claude-", "anthropic-")))

    def test_version_is_semver(self):
        self.assertRegex(load(PLUGIN)["version"], r"^\d+\.\d+\.\d+$")

    def test_entry_source_and_skills_path(self):
        entry = load(MARKET)["plugins"][0]
        self.assertEqual(entry["source"], "./")
        skills = load(PLUGIN)["skills"]
        skills = [skills] if isinstance(skills, str) else skills
        self.assertIn("./", skills)

    def test_marketplace_entry_has_no_version(self):
        self.assertNotIn("version", load(MARKET)["plugins"][0])

    def test_skill_folders_are_valid_names(self):
        folders = [d for d in sorted(os.listdir(ROOT))
                   if os.path.isfile(os.path.join(ROOT, d, "SKILL.md"))]
        self.assertTrue(folders)
        for d in folders:
            self.assertRegex(d, NAME_RE)
            self.assertNotEqual(d, "bin")

    def test_no_plugin_behaviour_files_at_root(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "bin")))
        self.assertFalse(os.path.exists(os.path.join(ROOT, "CLAUDE.md")))


if __name__ == "__main__":
    unittest.main()
