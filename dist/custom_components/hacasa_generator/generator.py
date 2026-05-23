"""Generate HaCasa dashboard YAML from JSON-like dashboard definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import unicodedata
from typing import Any, Iterable

import yaml

from .const import DASHBOARD_KEY_PREFIX, HACASA_TEMPLATE_INCLUDE

SUPPORTED_DOMAINS = {
    "binary_sensor",
    "climate",
    "cover",
    "fan",
    "light",
    "lock",
    "media_player",
    "number",
    "sensor",
    "switch",
    "vacuum",
}

DOMAIN_TEMPLATES = {
    "binary_sensor": "hc_sensor_card",
    "climate": "hc_climate_card",
    "cover": "custom_hc_cover_card",
    "fan": "hc_fan_card",
    "light": "hc_light_card",
    "lock": "hc_sensor_card",
    "media_player": "hc_media_card",
    "number": "hc_number_card",
    "sensor": "hc_sensor_card",
    "switch": "hc_switch_card",
    "vacuum": "hc_vacuum_card",
}


class TaggedScalar:
    """YAML scalar with a Home Assistant tag."""

    def __init__(self, tag: str, value: str) -> None:
        self.tag = tag
        self.value = value


class HaCasaDumper(yaml.SafeDumper):
    """YAML dumper that avoids anchors and supports HA tags."""

    def ignore_aliases(self, data: Any) -> bool:
        return True


def _represent_tagged_scalar(dumper: yaml.Dumper, data: TaggedScalar) -> yaml.Node:
    return dumper.represent_scalar(data.tag, data.value)


HaCasaDumper.add_representer(TaggedScalar, _represent_tagged_scalar)


@dataclass(frozen=True)
class GeneratedDashboard:
    """Generated dashboard files."""

    slug: str
    dashboard_key: str
    title: str
    icon: str
    filename: str
    files: list[str]


def make_slug(value: Any) -> str:
    """Create a stable URL/file-safe slug."""

    text = unicodedata.normalize("NFKD", str(value or "dashboard"))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "dashboard"


def dashboard_key_for_slug(slug: str) -> str:
    """Return the Lovelace dashboard key for a generated slug."""

    return f"{DASHBOARD_KEY_PREFIX}-{slug}"


def yaml_dump(data: Any) -> str:
    """Dump YAML with stable formatting."""

    return yaml.dump(
        data,
        Dumper=HaCasaDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Normalize and validate a dashboard generator configuration."""

    if not isinstance(config, dict):
        raise ValueError("Dashboard configuration must be a JSON object")

    name = str(config.get("name") or "").strip()
    if not name:
        raise ValueError("Dashboard configuration requires a non-empty name")

    rooms = config.get("rooms", [])
    if not isinstance(rooms, list):
        raise ValueError("rooms must be a list")

    normalized = {**config}
    normalized["name"] = name
    normalized["slug"] = make_slug(config.get("slug") or name)
    normalized["theme"] = config.get("theme") or "HaCasa Gold"
    normalized["icon"] = config.get("icon") or "mdi:view-dashboard"
    normalized["rooms"] = rooms
    return normalized


def resolve_dashboard_config(
    config: dict[str, Any], registry_entities: Iterable[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Resolve rooms against HA registry/entity data and explicit overrides."""

    normalized = normalize_config(config)
    registry = list(registry_entities or [])
    resolved_rooms = []

    for room in normalized["rooms"]:
        if not isinstance(room, dict):
            raise ValueError("Each room must be an object")
        room_name = str(room.get("name") or "").strip()
        if not room_name:
            raise ValueError("Each room requires a name")

        room_area = room.get("area")
        collected: dict[str, dict[str, Any]] = {}

        if room_area:
            for entity in registry:
                if _matches_area(entity, str(room_area)):
                    _add_entity(collected, entity)

        _merge_entity_spec(collected, room.get("entities"))
        _merge_entity_spec(collected, room.get("include"))

        for entity_id in _entity_ids_from_spec(room.get("exclude")):
            collected.pop(entity_id, None)

        overrides = room.get("overrides") if isinstance(room.get("overrides"), dict) else {}
        for entity_id, override in overrides.items():
            if entity_id in collected and isinstance(override, dict):
                collected[entity_id].update(override)

        entities_by_domain: dict[str, list[dict[str, Any]]] = {}
        for entity in sorted(collected.values(), key=lambda item: item["entity_id"]):
            domain = entity["entity_id"].split(".", 1)[0]
            if domain in SUPPORTED_DOMAINS:
                entities_by_domain.setdefault(domain, []).append(entity)

        resolved_rooms.append(
            {
                **room,
                "name": room_name,
                "path": room.get("path") or f"room-{make_slug(room_name)}",
                "icon": room.get("icon") or "mdi:sofa-outline",
                "entities_by_domain": entities_by_domain,
            }
        )

    return {**normalized, "rooms": resolved_rooms}


def write_dashboard(
    config: dict[str, Any],
    output_base_dir: str | Path,
    registry_entities: Iterable[dict[str, Any]] | None = None,
    config_root: str = "/config",
) -> GeneratedDashboard:
    """Generate and write a complete HaCasa dashboard folder."""

    resolved = resolve_dashboard_config(config, registry_entities)
    slug = resolved["slug"]
    dashboard_key = dashboard_key_for_slug(slug)
    output_dir = Path(output_base_dir) / slug
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files: list[str] = []

    def write(relative_path: str, data: Any) -> None:
        target = output_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml_dump(data), encoding="utf-8")
        files.append(str(target))

    include_root = f"{config_root}/dashboard/HaCasa/{slug}"
    main_views = [
        "views/main/00-overview.yaml",
        "views/main/01-rooms.yaml",
    ]
    room_views = [
        f"views/rooms/{index:02d}-{make_slug(room['name'])}.yaml"
        for index, room in enumerate(resolved["rooms"])
    ]

    write(
        "dashboard.yaml",
        {
            "title": resolved["name"],
            "theme": resolved["theme"],
            "button_card_templates": TaggedScalar(
                "!include_dir_merge_named", HACASA_TEMPLATE_INCLUDE
            ),
            "kiosk_mode": {
                "non_admin_settings": {
                    "hide_header": True,
                    "ignore_entity_settings": True,
                },
                "mobile_settings": {"hide_header": True},
            },
            "views": [
                TaggedScalar("!include", f"{include_root}/{path}")
                for path in [*main_views, *room_views]
            ],
        },
    )

    write("components/navigation/navbar.yaml", _navigation_bar(resolved, dashboard_key))
    write("components/popups/overview_lights.yaml", _entity_popup(resolved, "light"))
    write("components/popups/overview_climate.yaml", _entity_popup(resolved, "climate"))
    write("components/popups/overview_blinds.yaml", _entity_popup(resolved, "cover"))
    write("components/popups/overview_maintenance.yaml", _maintenance_popup(resolved))
    write("views/main/00-overview.yaml", _overview_view(resolved, include_root, dashboard_key))
    write("views/main/01-rooms.yaml", _rooms_view(resolved, include_root, dashboard_key))

    for index, room in enumerate(resolved["rooms"]):
        write(room_views[index], _room_view(resolved, room, include_root))

    return GeneratedDashboard(
        slug=slug,
        dashboard_key=dashboard_key,
        title=resolved["name"],
        icon=resolved["icon"],
        filename=f"dashboard/HaCasa/{slug}/dashboard.yaml",
        files=files,
    )


def _matches_area(entity: dict[str, Any], area: str) -> bool:
    candidates = {
        entity.get("area_id"),
        entity.get("area_name"),
        entity.get("device_area_id"),
        entity.get("device_area_name"),
    }
    return area in candidates or make_slug(area) in {make_slug(item) for item in candidates if item}


def _add_entity(target: dict[str, dict[str, Any]], entity: dict[str, Any]) -> None:
    entity_id = str(entity.get("entity_id") or "")
    if "." not in entity_id:
        return
    domain = entity_id.split(".", 1)[0]
    if domain not in SUPPORTED_DOMAINS:
        return
    target[entity_id] = {
        "entity_id": entity_id,
        "name": entity.get("name") or _friendly_name(entity_id),
        "icon": entity.get("icon"),
        "device_class": entity.get("device_class"),
    }


def _merge_entity_spec(target: dict[str, dict[str, Any]], spec: Any) -> None:
    if isinstance(spec, dict):
        for domain, values in spec.items():
            if domain in SUPPORTED_DOMAINS:
                for entity in _entities_from_values(values):
                    if entity["entity_id"].split(".", 1)[0] == domain:
                        target[entity["entity_id"]] = entity
            else:
                for entity in _entities_from_values(values):
                    target[entity["entity_id"]] = entity
    else:
        for entity in _entities_from_values(spec):
            target[entity["entity_id"]] = entity


def _entities_from_values(values: Any) -> list[dict[str, Any]]:
    if values is None:
        return []
    if isinstance(values, (str, dict)):
        values = [values]
    if not isinstance(values, list):
        return []

    entities = []
    for value in values:
        if isinstance(value, str):
            entities.append({"entity_id": value, "name": _friendly_name(value)})
        elif isinstance(value, dict) and isinstance(value.get("entity_id"), str):
            entity_id = value["entity_id"]
            entities.append(
                {
                    **value,
                    "entity_id": entity_id,
                    "name": value.get("name") or _friendly_name(entity_id),
                }
            )
    return entities


def _entity_ids_from_spec(spec: Any) -> set[str]:
    return {entity["entity_id"] for entity in _entities_from_values(spec)} | {
        entity["entity_id"] for entity in _flatten_dict_spec(spec)
    }


def _flatten_dict_spec(spec: Any) -> list[dict[str, Any]]:
    if not isinstance(spec, dict):
        return []
    entities = []
    for value in spec.values():
        entities.extend(_entities_from_values(value))
    return entities


def _friendly_name(entity_id: str) -> str:
    name = entity_id.split(".", 1)[-1]
    return name.replace("_", " ").title()


def _all_entities(config: dict[str, Any], domain: str | None = None) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    seen = set()
    for room in config["rooms"]:
        domains = [domain] if domain else list(room["entities_by_domain"])
        for current_domain in domains:
            for entity in room["entities_by_domain"].get(current_domain, []):
                if entity["entity_id"] not in seen:
                    entities.append({**entity, "room_name": room["name"]})
                    seen.add(entity["entity_id"])
    return entities


def _first_entity(config: dict[str, Any], domain: str) -> str | None:
    entities = _all_entities(config, domain)
    return entities[0]["entity_id"] if entities else None


def _navigation_bar(config: dict[str, Any], dashboard_key: str) -> dict[str, Any]:
    base = f"/{dashboard_key}"
    routes = [
        {
            "icon": "mdi:home-variant-outline",
            "icon_selected": "mdi:home-variant",
            "label": "Home",
            "url": f"{base}/overview",
            "haptic": "heavy",
        },
        {
            "icon": "mdi:sofa-outline",
            "icon_selected": "mdi:sofa",
            "label": "Rooms",
            "url": f"{base}/rooms",
            "haptic": "heavy",
        },
    ]
    for route in config.get("navigation") or []:
        if isinstance(route, dict) and route.get("url") and route.get("label"):
            routes.append(route)
    return {
        "type": "custom:navbar-card",
        "mobile": {"mode": "floating", "show_labels": False},
        "desktop": {
            "min_width": 1024,
            "mode": "floating",
            "position": "bottom",
            "show_labels": False,
        },
        "haptic": {
            "url": True,
            "tap_action": True,
            "hold_action": True,
            "double_tap_action": True,
        },
        "routes": routes,
        "styles": ".navbar-card.mobile.floating { width: fit-content; max-width: calc(100vw - 26px); }\n",
    }


def _overview_view(config: dict[str, Any], include_root: str, dashboard_key: str) -> dict[str, Any]:
    cards: list[Any] = [TaggedScalar("!include", f"{include_root}/components/navigation/navbar.yaml")]
    overview = config.get("overview") if isinstance(config.get("overview"), dict) else {}
    weather_entity = overview.get("weather_entity")
    if weather_entity:
        cards.append(
            {
                "type": "custom:button-card",
                "template": "hc_weather_card",
                "entity": weather_entity,
                "variables": {"show_forecast": True},
            }
        )

    nav_cards = []
    for domain, title, icon, popup_hash in [
        ("climate", "Climate", "mdi:thermostat", "#overview-climate"),
        ("light", "Iluminação", "mdi:lightbulb-group-outline", "#overview-lights"),
        ("cover", "Persianas", "mdi:window-shutter", "#overview-blinds"),
    ]:
        entities = _all_entities(config, domain)
        if entities:
            nav_cards.append(_overview_nav_card(title, icon, entities, popup_hash))

    battery_entities = _battery_entities(config)
    if battery_entities:
        nav_cards.append(
            _overview_nav_card("Manutenção", "mdi:wrench", battery_entities, "#overview-maintenance")
        )

    if nav_cards:
        cards.append({"type": "grid", "columns": 2, "square": False, "cards": nav_cards})

    for popup in ["overview_climate", "overview_lights", "overview_blinds", "overview_maintenance"]:
        cards.append(TaggedScalar("!include", f"{include_root}/components/popups/{popup}.yaml"))

    return {"title": "Home", "path": "overview", "icon": "mdi:home-variant", "cards": cards}


def _overview_nav_card(
    name: str, icon: str, entities: list[dict[str, Any]], navigation_path: str
) -> dict[str, Any]:
    ids = [entity["entity_id"] for entity in entities]
    return {
        "type": "custom:button-card",
        "template": "hc_navigation_card",
        "entity": ids[0],
        "name": name,
        "icon": icon,
        "label": _count_label_js(ids),
        "styles": {
            "icon": [{"color": "var(--color-orange)"}],
        },
        "tap_action": {
            "action": "navigate",
            "haptic": "heavy",
            "navigation_path": navigation_path,
        },
    }


def _rooms_view(config: dict[str, Any], include_root: str, dashboard_key: str) -> dict[str, Any]:
    base = f"/{dashboard_key}"
    cards: list[Any] = [TaggedScalar("!include", f"{include_root}/components/navigation/navbar.yaml")]
    room_cards = []
    for room in config["rooms"]:
        lights = room["entities_by_domain"].get("light", [])
        all_room_entities = [entity for values in room["entities_by_domain"].values() for entity in values]
        primary_entity = (lights or all_room_entities or [{"entity_id": "sun.sun"}])[0]["entity_id"]
        room_cards.append(
            {
                "type": "custom:button-card",
                "template": "hc_room_card",
                "entity": primary_entity,
                "name": room["name"],
                "icon": room["icon"],
                "variables": {
                    "light_entities": [entity["entity_id"] for entity in lights],
                    "lights_target_entity": primary_entity,
                },
                "tap_action": {
                    "action": "navigate",
                    "haptic": "heavy",
                    "navigation_path": f"{base}/{room['path']}",
                },
            }
        )
    cards.append({"type": "grid", "columns": 2, "square": False, "cards": room_cards})
    return {"title": "Rooms", "path": "rooms", "icon": "mdi:sofa", "cards": cards}


def _room_view(config: dict[str, Any], room: dict[str, Any], include_root: str) -> dict[str, Any]:
    cards: list[Any] = [
        TaggedScalar("!include", f"{include_root}/components/navigation/navbar.yaml"),
        _title_card(room["name"]),
    ]

    for domain, columns in [
        ("sensor", 2),
        ("binary_sensor", 2),
        ("lock", 1),
        ("cover", 1),
        ("climate", 1),
        ("fan", 1),
        ("switch", 2),
        ("media_player", 1),
        ("vacuum", 1),
        ("number", 2),
        ("light", 2),
    ]:
        entities = room["entities_by_domain"].get(domain, [])
        if entities:
            cards.append(
                {
                    "type": "grid",
                    "columns": columns,
                    "square": False,
                    "cards": [_entity_card(entity) for entity in entities],
                }
            )

    cards.append({"type": "custom:button-card", "color_type": "blank-card", "styles": {"card": [{"height": "100px"}]}})
    return {"title": room["name"], "path": room["path"], "subview": True, "cards": cards}


def _title_card(name: str) -> dict[str, Any]:
    return {
        "type": "custom:button-card",
        "name": name,
        "tap_action": {"action": "none", "haptic": "heavy"},
        "hold_action": {"action": "none", "haptic": "heavy"},
        "styles": {
            "card": [
                {"background": "none"},
                {"box-shadow": "none"},
                {"padding": 0},
                {"margin-bottom": "20px"},
            ],
            "grid": [{"grid-template-areas": "'n'"}, {"grid-template-columns": "1fr"}],
            "name": [
                {"justify-self": "start"},
                {"font-weight": 800},
                {"font-size": "25px"},
            ],
        },
    }


def _entity_card(entity: dict[str, Any]) -> dict[str, Any]:
    domain = entity["entity_id"].split(".", 1)[0]
    template = entity.get("template") or _sensor_template(entity) or DOMAIN_TEMPLATES[domain]
    card = {
        "type": "custom:button-card",
        "template": template,
        "entity": entity["entity_id"],
        "name": entity.get("name") or _friendly_name(entity["entity_id"]),
    }
    if entity.get("icon"):
        card["icon"] = entity["icon"]
    variables = entity.get("variables")
    if isinstance(variables, dict):
        card["variables"] = variables
    elif domain == "climate":
        card["variables"] = {"show_graph": False, "show_mode_buttons": True}
    return card


def _sensor_template(entity: dict[str, Any]) -> str | None:
    if entity["entity_id"].startswith("sensor.") and entity.get("device_class") == "battery":
        return "hc_battery_card"
    return None


def _entity_popup(config: dict[str, Any], domain: str) -> dict[str, Any]:
    entities = _all_entities(config, domain)
    names = {
        "light": ("#overview-lights", "Iluminação", "mdi:lightbulb-group-outline", "920px"),
        "climate": ("#overview-climate", "Climatização", "mdi:thermostat", "760px"),
        "cover": ("#overview-blinds", "Persianas", "mdi:window-shutter", "820px"),
    }
    popup_hash, name, icon, height = names[domain]
    primary = entities[0]["entity_id"] if entities else "sun.sun"
    cards = [_popup_header(popup_hash, primary, name, icon, height)]
    entity_cards = []
    for entity in entities:
        card = _entity_card({**entity, "name": f"{entity['name']} - {entity['room_name']}"})
        if domain == "light":
            entity_cards.append(
                {
                    "type": "conditional",
                    "conditions": [{"entity": entity["entity_id"], "state": "on"}],
                    "card": card,
                }
            )
        else:
            entity_cards.append(card)
    cards.append({"type": "vertical-stack", "cards": entity_cards})
    return {"type": "vertical-stack", "cards": cards}


def _maintenance_popup(config: dict[str, Any]) -> dict[str, Any]:
    entities = _battery_entities(config)
    primary = entities[0]["entity_id"] if entities else "sun.sun"
    return {
        "type": "vertical-stack",
        "cards": [
            _popup_header("#overview-maintenance", primary, "Manutenção", "mdi:wrench", "680px"),
            {
                "type": "grid",
                "columns": 2,
                "square": False,
                "cards": [_entity_card(entity) for entity in entities],
            },
        ],
    }


def _battery_entities(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entity
        for entity in _all_entities(config, "sensor")
        if entity.get("device_class") == "battery" or "battery" in entity["entity_id"]
    ]


def _popup_header(
    popup_hash: str, entity_id: str, name: str, icon: str, height: str
) -> dict[str, Any]:
    return {
        "type": "custom:bubble-card",
        "card_type": "pop-up",
        "hash": popup_hash,
        "button_type": "state",
        "entity": entity_id,
        "name": name,
        "icon": icon,
        "show_icon": True,
        "show_name": True,
        "show_state": True,
        "scrolling_effect": False,
        "close_by_clicking_outside": True,
        "styles": (
            ".bubble-pop-up {\n"
            f"  height: min({height}, calc(100vh - 100px)) !important;\n"
            "  margin: 50px 0 !important;\n"
            "  overflow-y: auto !important;\n"
            "}\n"
        ),
    }


def _count_label_js(entity_ids: list[str]) -> str:
    ids = ", ".join(repr(entity_id) for entity_id in entity_ids)
    return (
        "[[[\n"
        f"  const ids = [{ids}];\n"
        "  const active = ids.filter((id) => {\n"
        "    const state = states[id]?.state;\n"
        "    return state && !['off', 'closed', 'closing', 'unavailable', 'unknown'].includes(state);\n"
        "  }).length;\n"
        "  return active ? `${active} active` : 'All off';\n"
        "]]]\n"
    )
