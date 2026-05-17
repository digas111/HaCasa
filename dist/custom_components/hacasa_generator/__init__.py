"""HaCasa dashboard generator integration."""

from __future__ import annotations

from pathlib import Path
import inspect
from typing import Any

import voluptuous as vol

from homeassistant.components import panel_custom, websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er

from .config_patch import patch_lovelace_dashboard
from .const import (
    DASHBOARD_BASE_DIR,
    DATA_STORE,
    DOMAIN,
    PANEL_ELEMENT,
    PANEL_ICON,
    PANEL_TITLE,
    PANEL_URL,
    STATIC_URL,
)
from .generator import resolve_dashboard_config, write_dashboard
from .storage import HaCasaGeneratorStore

PLATFORMS: list[str] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HaCasa Generator from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    store = HaCasaGeneratorStore(hass)
    await store.async_load()
    hass.data[DOMAIN][DATA_STORE] = store

    await _async_register_static_path(hass)
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL,
        webcomponent_name=PANEL_ELEMENT,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{STATIC_URL}/panel.js",
        config={},
        require_admin=True,
    )
    if not hass.data[DOMAIN].get("websocket_registered"):
        _register_websocket_commands(hass)
        hass.data[DOMAIN]["websocket_registered"] = True
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload HaCasa Generator."""

    remove_result = panel_custom.async_remove_panel(hass, PANEL_URL)
    if inspect.isawaitable(remove_result):
        await remove_result
    hass.data.get(DOMAIN, {}).pop(DATA_STORE, None)
    return True


async def _async_register_static_path(hass: HomeAssistant) -> None:
    frontend_dir = Path(__file__).parent / "frontend"
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(frontend_dir), False)]
        )
    except (AttributeError, ImportError):
        hass.http.register_static_path(STATIC_URL, str(frontend_dir), False)


@callback
def _register_websocket_commands(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, _ws_list_configs)
    websocket_api.async_register_command(hass, _ws_get_config)
    websocket_api.async_register_command(hass, _ws_save_config)
    websocket_api.async_register_command(hass, _ws_delete_config)
    websocket_api.async_register_command(hass, _ws_preview)
    websocket_api.async_register_command(hass, _ws_render)


def _store(hass: HomeAssistant) -> HaCasaGeneratorStore:
    return hass.data[DOMAIN][DATA_STORE]


@websocket_api.websocket_command({vol.Required("type"): "hacasa_generator/list_configs"})
@websocket_api.async_response
async def _ws_list_configs(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.require_admin()
    connection.send_result(msg["id"], await _store(hass).async_list())


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/get_config",
        vol.Required("id"): str,
    }
)
@websocket_api.async_response
async def _ws_get_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.require_admin()
    item = await _store(hass).async_get(msg["id"])
    if item is None:
        connection.send_error(msg["id"], "not_found", "Dashboard configuration not found")
        return
    connection.send_result(msg["id"], item)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/save_config",
        vol.Optional("id"): str,
        vol.Required("config"): dict,
    }
)
@websocket_api.async_response
async def _ws_save_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.require_admin()
    try:
        item = await _store(hass).async_save_config(msg["config"], msg.get("id"))
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_config", str(err))
        return
    connection.send_result(msg["id"], item)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/delete_config",
        vol.Required("id"): str,
    }
)
@websocket_api.async_response
async def _ws_delete_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.require_admin()
    deleted = await _store(hass).async_delete(msg["id"])
    connection.send_result(msg["id"], {"deleted": deleted})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/preview",
        vol.Required("config"): dict,
    }
)
@websocket_api.async_response
async def _ws_preview(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.require_admin()
    try:
        resolved = resolve_dashboard_config(msg["config"], _registry_entities(hass))
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_config", str(err))
        return
    connection.send_result(
        msg["id"],
        {
            "name": resolved["name"],
            "slug": resolved["slug"],
            "rooms": [
                {
                    "name": room["name"],
                    "path": room["path"],
                    "entities_by_domain": room["entities_by_domain"],
                }
                for room in resolved["rooms"]
            ],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/render",
        vol.Optional("id"): str,
        vol.Required("config"): dict,
    }
)
@websocket_api.async_response
async def _ws_render(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.require_admin()
    try:
        item = await _store(hass).async_save_config(msg["config"], msg.get("id"))
        generated = write_dashboard(
            item["config"],
            hass.config.path(DASHBOARD_BASE_DIR),
            _registry_entities(hass),
            "/config",
        )
        patch = patch_lovelace_dashboard(
            hass.config.path("configuration.yaml"),
            generated.dashboard_key,
            generated.title,
            generated.icon,
            generated.filename,
        )
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_config", str(err))
        return

    connection.send_result(
        msg["id"],
        {
            "config": item,
            "dashboard_key": generated.dashboard_key,
            "dashboard_url": f"/{generated.dashboard_key}/overview",
            "filename": generated.filename,
            "files": generated.files,
            "config_patch": {
                "changed": patch.changed,
                "backup_path": patch.backup_path,
                "restart_required": patch.changed,
            },
        },
    )


def _registry_entities(hass: HomeAssistant) -> list[dict[str, Any]]:
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    area_registry = ar.async_get(hass)
    entities = []

    for entry in entity_registry.entities.values():
        entity_id = entry.entity_id
        domain = entity_id.split(".", 1)[0]
        state = hass.states.get(entity_id)
        device = device_registry.devices.get(entry.device_id) if entry.device_id else None
        area_id = entry.area_id or (device.area_id if device else None)
        area = area_registry.areas.get(area_id) if area_id else None
        device_area = area_registry.areas.get(device.area_id) if device and device.area_id else None

        entities.append(
            {
                "entity_id": entity_id,
                "domain": domain,
                "name": entry.name or entry.original_name or (state.name if state else None),
                "icon": entry.icon or (state.attributes.get("icon") if state else None),
                "device_class": state.attributes.get("device_class") if state else None,
                "area_id": area_id,
                "area_name": area.name if area else None,
                "device_area_id": device.area_id if device else None,
                "device_area_name": device_area.name if device_area else None,
            }
        )

    return entities
