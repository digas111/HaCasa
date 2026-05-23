from __future__ import annotations

from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hacasa_generator.const import DATA_STORE, DOMAIN, PANEL_ELEMENT, PANEL_URL

EXPECTED_WEBSOCKET_COMMANDS = {
    "_ws_list_configs",
    "_ws_get_config",
    "_ws_save_config",
    "_ws_delete_config",
    "_ws_preview",
    "_ws_render",
}


async def test_setup_entry_registers_panel_store_and_websocket_commands(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="HaCasa Generator", data={})
    entry.add_to_hass(hass)

    with (
        patch("custom_components.hacasa_generator._async_register_static_path", AsyncMock()) as register_static,
        patch("custom_components.hacasa_generator.panel_custom.async_register_panel", AsyncMock()) as register_panel,
        patch("custom_components.hacasa_generator.websocket_api.async_register_command") as register_command,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    register_static.assert_awaited_once()
    register_panel.assert_awaited_once()
    assert register_panel.call_args.kwargs["frontend_url_path"] == PANEL_URL
    assert register_panel.call_args.kwargs["webcomponent_name"] == PANEL_ELEMENT
    registered_commands = {
        name
        for call in register_command.call_args_list
        for name in [getattr(call.args[-1], "__name__", None)]
        if name
    }
    assert EXPECTED_WEBSOCKET_COMMANDS <= registered_commands
    assert DOMAIN in hass.data
    assert DATA_STORE in hass.data[DOMAIN]


async def test_unload_entry_removes_panel_and_store(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="HaCasa Generator", data={})
    entry.add_to_hass(hass)

    with (
        patch("custom_components.hacasa_generator._async_register_static_path", AsyncMock()),
        patch("custom_components.hacasa_generator.panel_custom.async_register_panel", AsyncMock()),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    with patch("custom_components.hacasa_generator.async_remove_frontend_panel") as remove_panel:
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

    remove_panel.assert_called_once_with(hass, PANEL_URL, warn_if_unknown=False)
    assert DATA_STORE not in hass.data[DOMAIN]
