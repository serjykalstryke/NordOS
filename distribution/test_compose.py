"""Offline checks for build selection, source ownership, and staged installation."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("compose", Path(__file__).with_name("compose.py"))
compose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compose)


class CompositionTests(unittest.TestCase):
    def test_selection_can_use_existing_sdk_or_include_dependencies(self):
        data = {"toolkit": {}, "framework": {"requires": ["toolkit"]},
                "core": {"requires": ["toolkit", "framework"]}}
        self.assertEqual(compose.select_components(data, "core", False), ["core"])
        self.assertEqual(compose.select_components(data, "core", True), ["toolkit", "framework", "core"])
        with self.assertRaises(compose.BuildError):
            compose.select_components(data, "unknown", False)

    def test_cycle_and_unknown_dependency_are_rejected(self):
        with self.assertRaises(compose.BuildError):
            compose.select_components({"a": {"requires": ["b"]}, "b": {"requires": ["a"]}}, None, False)
        with self.assertRaises(compose.BuildError):
            compose.select_components({"a": {"requires": ["missing"]}}, None, False)

    def test_owned_output_never_adopts_existing_contents(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)
            (path / "important").write_text("keep")
            with self.assertRaises(compose.BuildError):
                compose.ensure_workspace(path)
            self.assertEqual((path / "important").read_text(), "keep")

    def test_owned_workspace_and_foreign_marker(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "output"
            compose.ensure_workspace(path)
            compose.ensure_workspace(path)
            (path / compose.MARKER).write_text(json.dumps({"repository": "/different", "format": 1}))
            with self.assertRaises(compose.BuildError):
                compose.ensure_workspace(path)

    def test_stage_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "output"
            compose.ensure_workspace(path)
            (path / "stage").symlink_to(Path(root), target_is_directory=True)
            with self.assertRaises(compose.BuildError):
                compose.ensure_workspace(path)

    def test_environment_preserves_external_sdk_without_global_sysroot(self):
        with patch.dict(os.environ, {"PKG_CONFIG_PATH": "/sdk/pkgconfig", "CMAKE_PREFIX_PATH": "/sdk",
                                     "DESTDIR": "/unwanted"}, clear=True):
            env = compose.build_environment(Path("/output"))
        self.assertEqual(env["CMAKE_PREFIX_PATH"], "/output/stage/usr:/sdk")
        self.assertTrue(env["PKG_CONFIG_PATH"].endswith(":/sdk/pkgconfig"))
        self.assertNotIn("PKG_CONFIG_SYSROOT_DIR", env)
        self.assertNotIn("DESTDIR", env)

    def test_duplicate_or_invalid_source_override_is_rejected(self):
        with self.assertRaises(compose.BuildError):
            compose.source_overrides(["core=/a", "core=/b"], {"core": {}})
        with self.assertRaises(compose.BuildError):
            compose.source_overrides(["../core=/a"], {"core": {}})

    @unittest.skipUnless(shutil.which("git"), "git unavailable")
    def test_pinned_external_sources_and_local_core_changes(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)
            (source / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.22)\nproject(Fixture NONE)\n")
            subprocess.run(["git", "init", "--quiet", str(source)], check=True)
            subprocess.run(["git", "-C", str(source), "add", "CMakeLists.txt"], check=True)
            subprocess.run(["git", "-C", str(source), "-c", "user.name=Build test", "-c",
                            "user.email=build@example.invalid", "commit", "--quiet", "-m", "Fixture"], check=True)
            revision = compose.git(source, "rev-parse", "HEAD")
            entry = {"name": "fixture", "revision": revision, "url": "https://example.invalid/fixture"}
            self.assertFalse(compose.source_record("fixture", entry, source)["working_tree_modified"])
            with self.assertRaises(compose.BuildError):
                compose.source_record("fixture", dict(entry, revision="0" * 40), source)
            (source / "new-source.cpp").write_text("// New source\n")
            with self.assertRaises(compose.BuildError):
                compose.source_record("fixture", entry, source)
            record = compose.source_record("core", {"name": "core", "local": ".."}, source)
            self.assertTrue(record["working_tree_modified"])
            self.assertIn("new-source.cpp", record["untracked_files"])
            self.assertEqual(len(record["tracked_diff_sha256"]), 64)

    @unittest.skipUnless(shutil.which("cmake") and shutil.which("make"), "CMake/Make unavailable")
    def test_real_cmake_install_stays_in_stage_even_for_absolute_destination(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "source"
            source.mkdir()
            (source / "fixture.txt").write_text("staged payload\n")
            (source / "CMakeLists.txt").write_text(
                'cmake_minimum_required(VERSION 3.22)\nproject(Fixture NONE)\n'
                'install(FILES fixture.txt DESTINATION /usr/share/nordos-compose-test)\n')
            workspace = compose.ensure_workspace(Path(root) / "output")
            compose.build_component("fixture", source, workspace, "Unix Makefiles", 1,
                                    compose.build_environment(workspace))
            staged = workspace / "stage/usr/share/nordos-compose-test/fixture.txt"
            self.assertEqual(staged.read_text(), "staged payload\n")


if __name__ == "__main__":
    unittest.main()
