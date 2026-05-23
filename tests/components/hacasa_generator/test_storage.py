from __future__ import annotations

import pytest

from custom_components.hacasa_generator.storage import HaCasaGeneratorStore


async def test_load_empty_storage(hass) -> None:
    store = HaCasaGeneratorStore(hass)

    await store.async_load()

    assert await store.async_list() == []


async def test_list_skips_malformed_storage_items(hass) -> None:
    store = HaCasaGeneratorStore(hass)
    store._data = {
        "configs": [
            {},
            {"id": "missing-name", "slug": "missing-name"},
            {
                "id": "bd-mobile",
                "name": "BD Mobile",
                "slug": "bd-mobile",
                "updated_at": "2026-05-20T00:00:00+00:00",
            },
        ]
    }

    assert await store.async_list() == [
        {
            "id": "bd-mobile",
            "name": "BD Mobile",
            "slug": "bd-mobile",
            "updated_at": "2026-05-20T00:00:00+00:00",
        }
    ]


async def test_save_update_and_get_config(hass) -> None:
    store = HaCasaGeneratorStore(hass)
    await store.async_load()

    created = await store.async_save_config({"name": "BD Mobile"})
    updated = await store.async_save_config({"name": "BD Mobile Updated"}, created["id"])

    assert created["id"] == "bd-mobile"
    assert updated["id"] == "bd-mobile"
    assert updated["name"] == "BD Mobile Updated"
    assert updated["slug"] == "bd-mobile-updated"
    assert updated["config"]["name"] == "BD Mobile Updated"
    assert updated["config"]["slug"] == "bd-mobile-updated"
    assert await store.async_get("bd-mobile") == updated
    assert await store.async_list() == [
        {
            "id": "bd-mobile",
            "name": "BD Mobile Updated",
            "slug": "bd-mobile-updated",
            "updated_at": updated["updated_at"],
        }
    ]


async def test_save_update_preserves_explicit_slug(hass) -> None:
    store = HaCasaGeneratorStore(hass)
    await store.async_load()

    created = await store.async_save_config({"name": "BD Mobile"})
    updated = await store.async_save_config(
        {"name": "BD Mobile Updated", "slug": "custom-mobile"},
        created["id"],
    )

    assert updated["id"] == "bd-mobile"
    assert updated["slug"] == "custom-mobile"
    assert updated["config"]["slug"] == "custom-mobile"


async def test_save_uses_unique_slug_for_new_configs(hass) -> None:
    store = HaCasaGeneratorStore(hass)
    await store.async_load()

    first = await store.async_save_config({"name": "BD Mobile"})
    second = await store.async_save_config({"name": "BD Mobile"})

    assert first["id"] == "bd-mobile"
    assert second["id"] == "bd-mobile-2"
    assert second["config"]["slug"] == "bd-mobile-2"


async def test_save_requires_name(hass) -> None:
    store = HaCasaGeneratorStore(hass)
    await store.async_load()

    with pytest.raises(ValueError, match="Dashboard configuration requires a non-empty name"):
        await store.async_save_config({"name": " "})


async def test_delete_config(hass) -> None:
    store = HaCasaGeneratorStore(hass)
    await store.async_load()
    created = await store.async_save_config({"name": "BD Mobile"})

    assert not await store.async_delete("missing")
    assert await store.async_delete(created["id"])
    assert await store.async_list() == []
