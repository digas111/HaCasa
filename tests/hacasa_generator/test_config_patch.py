import tempfile
import textwrap
import unittest
from pathlib import Path

from .helpers import import_generator_module

patch_lovelace_dashboard = import_generator_module("config_patch").patch_lovelace_dashboard


class ConfigPatchTest(unittest.TestCase):
    def test_add_dashboard_preserves_includes(self):
        source = textwrap.dedent(
            """
            default_config:

            frontend:
              themes: !include_dir_merge_named themes

            light: !include lights.yaml

            lovelace:
              mode: storage
              dashboards:
                lovelace-test:
                  mode: yaml
                  title: Test
                  icon: mdi:script
                  show_in_sidebar: true
                  filename: "dashboard/julian/dashboard.yaml"
            """
        ).lstrip()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "configuration.yaml"
            path.write_text(source, encoding="utf-8")
            result = patch_lovelace_dashboard(
                path,
                "hacasa-bd-mobile",
                "BD Mobile",
                "mdi:view-dashboard",
                "dashboard/HaCasa/bd-mobile/dashboard.yaml",
            )

            updated = path.read_text(encoding="utf-8")
            self.assertTrue(result.changed)
            self.assertTrue(Path(result.backup_path).exists())
            self.assertIn("themes: !include_dir_merge_named themes", updated)
            self.assertIn("light: !include lights.yaml", updated)
            self.assertIn("hacasa-bd-mobile:", updated)
            self.assertIn('filename: "dashboard/HaCasa/bd-mobile/dashboard.yaml"', updated)

    def test_update_existing_dashboard_is_idempotent(self):
        source = textwrap.dedent(
            """
            lovelace:
              mode: storage
              dashboards:
                hacasa-old:
                  mode: yaml
                  title: Old
                  icon: mdi:script
                  show_in_sidebar: true
                  filename: "dashboard/old.yaml"
            """
        ).lstrip()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "configuration.yaml"
            path.write_text(source, encoding="utf-8")
            first = patch_lovelace_dashboard(
                path,
                "hacasa-old",
                "New",
                "mdi:view-dashboard",
                "dashboard/HaCasa/new/dashboard.yaml",
            )
            second = patch_lovelace_dashboard(
                path,
                "hacasa-old",
                "New",
                "mdi:view-dashboard",
                "dashboard/HaCasa/new/dashboard.yaml",
            )

            updated = path.read_text(encoding="utf-8")
            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertEqual(updated.count("hacasa-old:"), 1)
            self.assertIn('title: "New"', updated)


if __name__ == "__main__":
    unittest.main()
