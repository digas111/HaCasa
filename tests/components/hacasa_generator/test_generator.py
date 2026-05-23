from __future__ import annotations

from pathlib import Path

import pytest

from custom_components.hacasa_generator.generator import (
    make_slug,
    resolve_dashboard_config,
    write_dashboard,
)


def test_slug_generation() -> None:
    assert make_slug("Sala e Cozinha") == "sala-e-cozinha"
    assert make_slug("  Geracao Arvore  ") == "geracao-arvore"
    assert make_slug("") == "dashboard"


def test_hybrid_area_and_explicit_entities() -> None:
    config = {
        "name": "BD Mobile",
        "rooms": [
            {
                "name": "Sala",
                "area": "sala",
                "entities": {
                    "light": [
                        {
                            "entity_id": "light.manual_lamp",
                            "name": "Manual Lamp",
                        }
                    ]
                },
                "exclude": ["light.excluded"],
                "overrides": {
                    "light.area_lamp": {"name": "Area Lamp Override"},
                },
            }
        ],
    }
    registry = [
        {"entity_id": "light.area_lamp", "area_id": "sala", "name": "Area Lamp"},
        {"entity_id": "light.excluded", "area_id": "sala", "name": "Excluded"},
        {"entity_id": "cover.window", "area_id": "sala", "name": "Window"},
        {"entity_id": "automation.skip_me", "area_id": "sala", "name": "Skip"},
    ]

    resolved = resolve_dashboard_config(config, registry)
    room = resolved["rooms"][0]
    lights = room["entities_by_domain"]["light"]

    assert [entity["entity_id"] for entity in lights] == ["light.area_lamp", "light.manual_lamp"]
    assert lights[0]["name"] == "Area Lamp Override"
    assert room["entities_by_domain"]["cover"][0]["entity_id"] == "cover.window"


def test_write_dashboard_files_without_helper_entities(tmp_path: Path) -> None:
    config = {
        "name": "Generated Test",
        "overview": {"weather_entity": "sensor.weather_entity_forecast"},
        "rooms": [
            {
                "name": "Office",
                "entities": {
                    "light": ["light.office_main", "light.office_desk"],
                    "sensor": [{"entity_id": "sensor.remote_battery", "device_class": "battery"}],
                },
            }
        ],
    }

    generated = write_dashboard(config, tmp_path)
    dashboard = tmp_path / generated.slug / "dashboard.yaml"
    room_view = tmp_path / generated.slug / "views/rooms/00-office.yaml"
    source = "\n".join(path.read_text() for path in Path(tmp_path, generated.slug).rglob("*.yaml"))

    assert dashboard.exists()
    assert "theme: HaCasa Gold" in dashboard.read_text(encoding="utf-8")
    assert room_view.exists()
    assert "platform: group" not in source
    assert "light.office_main" in source
    assert "hc_battery_card" in source


def test_invalid_config() -> None:
    with pytest.raises(ValueError):
        resolve_dashboard_config({"rooms": []})
