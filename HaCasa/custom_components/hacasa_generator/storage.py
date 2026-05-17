"""Persistent storage for HaCasa generator configurations."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION
from .generator import make_slug


class HaCasaGeneratorStore:
    """Store JSON dashboard configurations in Home Assistant storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = Store[dict[str, Any]](hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"configs": []}

    async def async_load(self) -> None:
        """Load storage data."""

        data = await self._store.async_load()
        if isinstance(data, dict) and isinstance(data.get("configs"), list):
            self._data = data

    async def async_list(self) -> list[dict[str, Any]]:
        """Return configuration summaries."""

        return [
            {
                "id": item["id"],
                "name": item["name"],
                "slug": item["slug"],
                "updated_at": item.get("updated_at"),
            }
            for item in self._data["configs"]
        ]

    async def async_get(self, config_id: str) -> dict[str, Any] | None:
        """Return a full stored configuration."""

        for item in self._data["configs"]:
            if item["id"] == config_id:
                return deepcopy(item)
        return None

    async def async_save_config(
        self, config: dict[str, Any], config_id: str | None = None
    ) -> dict[str, Any]:
        """Create or update a dashboard configuration."""

        name = str(config.get("name") or "").strip()
        if not name:
            raise ValueError("Dashboard configuration requires a non-empty name")

        slug = make_slug(config.get("slug") or name)
        now = datetime.now(UTC).isoformat()

        configs = self._data["configs"]
        if config_id:
            for index, item in enumerate(configs):
                if item["id"] == config_id:
                    configs[index] = {
                        **item,
                        "name": name,
                        "slug": slug,
                        "config": deepcopy(config),
                        "updated_at": now,
                    }
                    await self._store.async_save(self._data)
                    return deepcopy(configs[index])

        existing_slugs = {item["slug"] for item in configs}
        unique_slug = slug
        suffix = 2
        while unique_slug in existing_slugs:
            unique_slug = f"{slug}-{suffix}"
            suffix += 1

        item = {
            "id": unique_slug,
            "name": name,
            "slug": unique_slug,
            "config": deepcopy({**config, "slug": unique_slug}),
            "created_at": now,
            "updated_at": now,
        }
        configs.append(item)
        await self._store.async_save(self._data)
        return deepcopy(item)

    async def async_delete(self, config_id: str) -> bool:
        """Delete a stored dashboard configuration."""

        configs = self._data["configs"]
        new_configs = [item for item in configs if item["id"] != config_id]
        if len(new_configs) == len(configs):
            return False
        self._data["configs"] = new_configs
        await self._store.async_save(self._data)
        return True
