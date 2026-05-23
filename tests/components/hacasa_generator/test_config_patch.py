from __future__ import annotations

from pathlib import Path
import textwrap

from custom_components.hacasa_generator.config_patch import (
    patch_frontend_themes,
    patch_lovelace_dashboard,
)


def test_add_dashboard_preserves_includes(tmp_path: Path) -> None:
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

    config_path = tmp_path / "configuration.yaml"
    config_path.write_text(source, encoding="utf-8")
    result = patch_lovelace_dashboard(
        config_path,
        "hacasa-bd-mobile",
        "BD Mobile",
        "mdi:view-dashboard",
        "dashboard/HaCasa/bd-mobile/dashboard.yaml",
    )

    updated = config_path.read_text(encoding="utf-8")
    assert result.changed
    assert Path(result.backup_path).exists()
    assert "themes: !include_dir_merge_named themes" in updated
    assert "light: !include lights.yaml" in updated
    assert "hacasa-bd-mobile:" in updated
    assert 'filename: "dashboard/HaCasa/bd-mobile/dashboard.yaml"' in updated


def test_update_existing_dashboard_is_idempotent(tmp_path: Path) -> None:
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

    config_path = tmp_path / "configuration.yaml"
    config_path.write_text(source, encoding="utf-8")
    first = patch_lovelace_dashboard(
        config_path,
        "hacasa-old",
        "New",
        "mdi:view-dashboard",
        "dashboard/HaCasa/new/dashboard.yaml",
    )
    second = patch_lovelace_dashboard(
        config_path,
        "hacasa-old",
        "New",
        "mdi:view-dashboard",
        "dashboard/HaCasa/new/dashboard.yaml",
    )

    updated = config_path.read_text(encoding="utf-8")
    assert first.changed
    assert not second.changed
    assert updated.count("hacasa-old:") == 1
    assert 'title: "New"' in updated


def test_patch_frontend_themes_adds_frontend_block(tmp_path: Path) -> None:
    config_path = tmp_path / "configuration.yaml"
    config_path.write_text("default_config:\n", encoding="utf-8")

    first = patch_frontend_themes(config_path)
    second = patch_frontend_themes(config_path)

    updated = config_path.read_text(encoding="utf-8")
    assert first.changed
    assert not second.changed
    assert "frontend:\n  themes: !include_dir_merge_named themes\n" in updated


def test_patch_frontend_themes_preserves_existing_theme_include(tmp_path: Path) -> None:
    source = textwrap.dedent(
        """
        frontend:
          themes: !include_dir_merge_named themes
          extra_module_url:
            - /hacsfiles/HaCasa/HaCasa.js
        """
    ).lstrip()

    config_path = tmp_path / "configuration.yaml"
    config_path.write_text(source, encoding="utf-8")
    result = patch_frontend_themes(config_path)

    assert not result.changed
    assert config_path.read_text(encoding="utf-8") == source
