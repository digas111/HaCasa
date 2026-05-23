from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.exceptions import Unauthorized
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hacasa_generator import _ws_list_configs
from custom_components.hacasa_generator.const import DOMAIN


async def setup_generator(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="HaCasa Generator", data={})
    entry.add_to_hass(hass)

    with (
        patch("custom_components.hacasa_generator._async_register_static_path", AsyncMock()),
        patch("custom_components.hacasa_generator.panel_custom.async_register_panel", AsyncMock()),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()


async def receive_result(client, payload: dict) -> dict:
    await client.send_json(payload)
    return await client.receive_json()


async def test_websocket_commands_require_admin(hass) -> None:
    await setup_generator(hass)
    connection = MagicMock()
    connection.user.is_admin = False

    with pytest.raises(Unauthorized):
        await _ws_list_configs(hass, connection, {"id": 1})


async def test_websocket_save_list_get_and_delete(hass, hass_ws_client) -> None:
    await setup_generator(hass)
    client = await hass_ws_client(hass)

    save = await receive_result(
        client,
        {
            "id": 1,
            "type": "hacasa_generator/save_config",
            "config": {"name": "BD Mobile"},
        },
    )
    assert save["success"]
    config_id = save["result"]["id"]

    listed = await receive_result(client, {"id": 2, "type": "hacasa_generator/list_configs"})
    assert listed["success"]
    assert listed["result"][0]["id"] == config_id

    fetched = await receive_result(
        client,
        {
            "id": 3,
            "type": "hacasa_generator/get_config",
            "config_id": config_id,
        },
    )
    assert fetched["success"]
    assert fetched["result"]["name"] == "BD Mobile"

    deleted = await receive_result(
        client,
        {
            "id": 4,
            "type": "hacasa_generator/delete_config",
            "config_id": config_id,
        },
    )
    assert deleted["success"]
    assert deleted["result"] == {"deleted": True}


async def test_websocket_get_missing_returns_error(hass, hass_ws_client) -> None:
    await setup_generator(hass)
    client = await hass_ws_client(hass)

    result = await receive_result(
        client,
        {
            "id": 1,
            "type": "hacasa_generator/get_config",
            "config_id": "missing",
        },
    )

    assert not result["success"]
    assert result["error"]["code"] == "not_found"


async def test_websocket_preview_returns_resolved_rooms(hass, hass_ws_client) -> None:
    await setup_generator(hass)
    client = await hass_ws_client(hass)

    result = await receive_result(
        client,
        {
            "id": 1,
            "type": "hacasa_generator/preview",
            "config": {
                "name": "BD Mobile",
                "rooms": [
                    {
                        "name": "Office",
                        "entities": {"light": ["light.office_main"]},
                    }
                ],
            },
        },
    )

    assert result["success"]
    assert result["result"]["slug"] == "bd-mobile"
    assert result["result"]["rooms"][0]["entities_by_domain"]["light"][0]["entity_id"] == "light.office_main"


async def test_websocket_preview_invalid_config_returns_error(hass, hass_ws_client) -> None:
    await setup_generator(hass)
    client = await hass_ws_client(hass)

    result = await receive_result(
        client,
        {
            "id": 1,
            "type": "hacasa_generator/preview",
            "config": {},
        },
    )

    assert not result["success"]
    assert result["error"]["code"] == "invalid_config"


async def test_websocket_render_writes_dashboard_and_patches_config(hass, hass_ws_client) -> None:
    await setup_generator(hass)
    Path(hass.config.path("configuration.yaml")).write_text("lovelace:\n  mode: storage\n", encoding="utf-8")
    hacs_theme_dir = Path(hass.config.path("www/community/HaCasa/themes/HaCasa"))
    hacs_theme_dir.mkdir(parents=True, exist_ok=True)
    (hacs_theme_dir / "hacasa-gold.yaml").write_text("HaCasa Gold:\n  primary-color: gold\n", encoding="utf-8")
    target_theme = Path(hass.config.path("themes/HaCasa/hacasa-gold.yaml"))
    if target_theme.exists():
        target_theme.unlink()
    client = await hass_ws_client(hass)

    result = await receive_result(
        client,
        {
            "id": 1,
            "type": "hacasa_generator/render",
            "config": {
                "name": "BD Mobile",
                "rooms": [
                    {
                        "name": "Office",
                        "entities": {"light": ["light.office_main"]},
                    }
                ],
            },
        },
    )

    assert result["success"]
    assert result["result"]["dashboard_key"] == "hacasa-bd-mobile"
    assert result["result"]["dashboard_url"] == "/hacasa-bd-mobile/overview"
    assert result["result"]["config_patch"]["changed"]
    assert result["result"]["config_patch"]["restart_required"]
    assert result["result"]["config_patch"]["themes_installed"]
    assert Path(hass.config.path("dashboard/HaCasa/bd-mobile/dashboard.yaml")).exists()
    assert Path(hass.config.path("themes/HaCasa/hacasa-gold.yaml")).exists()
    config_source = Path(hass.config.path("configuration.yaml")).read_text(encoding="utf-8")
    assert "hacasa-bd-mobile:" in config_source
    assert "themes: !include_dir_merge_named themes" in config_source


async def test_websocket_render_renames_dashboard_folder_when_name_changes(
    hass, hass_ws_client
) -> None:
    await setup_generator(hass)
    Path(hass.config.path("configuration.yaml")).write_text(
        "lovelace:\n  mode: storage\n",
        encoding="utf-8",
    )
    client = await hass_ws_client(hass)

    first = await receive_result(
        client,
        {
            "id": 1,
            "type": "hacasa_generator/render",
            "config": {
                "name": "BD Mobile",
                "rooms": [
                    {
                        "name": "Office",
                        "entities": {"light": ["light.office_main"]},
                    }
                ],
            },
        },
    )

    result = await receive_result(
        client,
        {
            "id": 2,
            "type": "hacasa_generator/render",
            "config_id": first["result"]["config"]["id"],
            "config": {
                **first["result"]["config"]["config"],
                "name": "BD Mobile Updated",
            },
        },
    )

    config_source = Path(hass.config.path("configuration.yaml")).read_text(encoding="utf-8")
    assert result["success"]
    assert result["result"]["dashboard_key"] == "hacasa-bd-mobile-updated"
    assert Path(hass.config.path("dashboard/HaCasa/bd-mobile-updated/dashboard.yaml")).exists()
    assert not Path(hass.config.path("dashboard/HaCasa/bd-mobile")).exists()
    assert "hacasa-bd-mobile-updated:" in config_source
    assert "hacasa-bd-mobile:" not in config_source
