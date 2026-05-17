"""Constants for the HaCasa dashboard generator integration."""

from __future__ import annotations

DOMAIN = "hacasa_generator"
DATA_STORE = "store"

PANEL_URL = "hacasa-generator"
PANEL_TITLE = "HaCasa Generator"
PANEL_ICON = "mdi:view-dashboard-edit"
PANEL_ELEMENT = "hacasa-generator-panel"
STATIC_URL = "/hacasa_generator_static"

STORAGE_KEY = f"{DOMAIN}.configs"
STORAGE_VERSION = 1

DASHBOARD_BASE_DIR = "dashboard/HaCasa"
DASHBOARD_KEY_PREFIX = "hacasa"
HACASA_TEMPLATE_INCLUDE = "/config/dashboard/HaCasa/templates/"
