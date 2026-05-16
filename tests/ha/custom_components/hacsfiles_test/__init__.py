from pathlib import Path

from homeassistant.components.http import StaticPathConfig

DOMAIN = "hacsfiles_test"


async def async_setup(hass, config):
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/hacsfiles", Path(hass.config.path("www/community")), True)],
    )
    return True
