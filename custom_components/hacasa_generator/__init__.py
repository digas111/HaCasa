"""HaCasa dashboard generator integration."""

from __future__ import annotations

from pathlib import Path
import inspect
import re
import shutil
from typing import Any

import voluptuous as vol

from homeassistant.components import panel_custom, websocket_api
from homeassistant.components.frontend import async_remove_panel as async_remove_frontend_panel
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er

from .config_patch import patch_frontend_themes, patch_lovelace_dashboard
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
from .generator import dashboard_key_for_slug, resolve_dashboard_config, write_dashboard
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

    remove_panel = getattr(panel_custom, "async_remove_panel", None)
    remove_result = (
        remove_panel(hass, PANEL_URL)
        if remove_panel
        else async_remove_frontend_panel(hass, PANEL_URL, warn_if_unknown=False)
    )
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


@websocket_api.require_admin
@websocket_api.async_response
@websocket_api.websocket_command({vol.Required("type"): "hacasa_generator/list_configs"})
async def _ws_list_configs(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.send_result(msg["id"], await _store(hass).async_list())


@websocket_api.require_admin
@websocket_api.async_response
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/get_config",
        vol.Required("config_id"): str,
    }
)
async def _ws_get_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    item = await _store(hass).async_get(msg["config_id"])
    if item is None:
        connection.send_error(msg["id"], "not_found", "Dashboard configuration not found")
        return
    connection.send_result(msg["id"], item)


@websocket_api.require_admin
@websocket_api.async_response
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/save_config",
        vol.Optional("config_id"): str,
        vol.Required("config"): dict,
    }
)
async def _ws_save_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    try:
        item = await _store(hass).async_save_config(msg["config"], msg.get("config_id"))
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_config", str(err))
        return
    connection.send_result(msg["id"], item)


@websocket_api.require_admin
@websocket_api.async_response
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/delete_config",
        vol.Required("config_id"): str,
    }
)
async def _ws_delete_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    deleted = await _store(hass).async_delete(msg["config_id"])
    connection.send_result(msg["id"], {"deleted": deleted})


@websocket_api.require_admin
@websocket_api.async_response
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/preview",
        vol.Required("config"): dict,
    }
)
async def _ws_preview(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
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


@websocket_api.require_admin
@websocket_api.async_response
@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacasa_generator/render",
        vol.Optional("config_id"): str,
        vol.Required("config"): dict,
    }
)
async def _ws_render(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    try:
        previous_item = (
            await _store(hass).async_get(msg["config_id"]) if msg.get("config_id") else None
        )
        previous_slug = previous_item.get("slug") if previous_item else None
        item = await _store(hass).async_save_config(msg["config"], msg.get("config_id"))
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
            previous_dashboard_key=(
                dashboard_key_for_slug(previous_slug)
                if previous_slug and previous_slug != generated.slug
                else None
            ),
        )
        themes_installed = _install_themes(hass)
        frontend_patch = patch_frontend_themes(hass.config.path("configuration.yaml"))
        if previous_slug and previous_slug != generated.slug:
            previous_dir = Path(hass.config.path(DASHBOARD_BASE_DIR)) / previous_slug
            if previous_dir.exists():
                shutil.rmtree(previous_dir)
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
                "changed": patch.changed or frontend_patch.changed or themes_installed,
                "backup_path": frontend_patch.backup_path or patch.backup_path,
                "restart_required": patch.changed or frontend_patch.changed or themes_installed,
                "themes_installed": themes_installed,
                "themes_path": frontend_patch.themes_path,
            },
        },
    )


def _install_themes(hass: HomeAssistant) -> bool:
    """Install bundled HaCasa themes into Home Assistant's standard themes folder."""

    source_candidates = [
        Path(hass.config.path("www/community/HaCasa/themes/HaCasa")),
        Path(__file__).parent / "themes/HaCasa",
    ]
    source_dir = next((path for path in source_candidates if path.exists()), None)
    if source_dir is None:
        return False

    target_dir = Path(hass.config.path(_configured_themes_dir(hass), "HaCasa"))
    changed = False
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_file in source_dir.glob("*.yaml"):
        target_file = target_dir / source_file.name
        source = source_file.read_bytes()
        if target_file.exists() and target_file.read_bytes() == source:
            continue
        target_file.write_bytes(source)
        changed = True

    return changed


def _configured_themes_dir(hass: HomeAssistant) -> str:
    config_path = Path(hass.config.path("configuration.yaml"))
    if not config_path.exists():
        return "themes"

    source = config_path.read_text(encoding="utf-8")
    match = re.search(
        r"(?m)^\s+themes:\s+!include_dir_merge_named\s+['\"]?([^'\"\n]+)['\"]?\s*$",
        source,
    )
    if not match:
        return "themes"
    return match.group(1).strip()


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
