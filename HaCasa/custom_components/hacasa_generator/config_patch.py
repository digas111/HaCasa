"""Patch Home Assistant YAML config so generated dashboards are registered."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil

import yaml


@dataclass(frozen=True)
class ConfigPatchResult:
    """Result of a Home Assistant configuration patch."""

    changed: bool
    backup_path: str | None
    dashboard_key: str
    filename: str


def _quote(value: str) -> str:
    return yaml.safe_dump(value, default_style='"').strip()


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_top_level(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#") and _line_indent(line) == 0


def _entry_lines(
    dashboard_key: str, title: str, icon: str, filename: str, show_in_sidebar: bool
) -> list[str]:
    return [
        f"    {dashboard_key}:\n",
        "      mode: yaml\n",
        f"      title: {_quote(title)}\n",
        f"      icon: {_quote(icon)}\n",
        f"      show_in_sidebar: {str(show_in_sidebar).lower()}\n",
        f"      filename: {_quote(filename)}\n",
    ]


def patch_lovelace_dashboard(
    config_path: str | Path,
    dashboard_key: str,
    title: str,
    icon: str,
    filename: str,
    show_in_sidebar: bool = True,
) -> ConfigPatchResult:
    """Add or update a YAML Lovelace dashboard entry in configuration.yaml.

    The patch is intentionally line-based so existing includes and comments remain
    intact. A timestamped backup is created only when a write is needed.
    """

    path = Path(config_path)
    source = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = source.splitlines(keepends=True)
    entry = _entry_lines(dashboard_key, title, icon, filename, show_in_sidebar)

    if not lines:
        lines = ["lovelace:\n", "  mode: storage\n", "  dashboards:\n", *entry]
        return _write_if_changed(path, source, lines, dashboard_key, filename)

    lovelace_start = next(
        (index for index, line in enumerate(lines) if line.startswith("lovelace:")),
        None,
    )
    if lovelace_start is None:
        if lines[-1] and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.extend(["\n", "lovelace:\n", "  mode: storage\n", "  dashboards:\n", *entry])
        return _write_if_changed(path, source, lines, dashboard_key, filename)

    lovelace_end = len(lines)
    for index in range(lovelace_start + 1, len(lines)):
        if _is_top_level(lines[index]):
            lovelace_end = index
            break

    dashboards_start = None
    for index in range(lovelace_start + 1, lovelace_end):
        if _line_indent(lines[index]) == 2 and lines[index].lstrip().startswith("dashboards:"):
            dashboards_start = index
            break

    if dashboards_start is None:
        insert_at = lovelace_end
        lines[insert_at:insert_at] = ["  dashboards:\n", *entry]
        return _write_if_changed(path, source, lines, dashboard_key, filename)

    dashboards_end = lovelace_end
    for index in range(dashboards_start + 1, lovelace_end):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#") and _line_indent(lines[index]) <= 2:
            dashboards_end = index
            break

    key_line = f"{dashboard_key}:"
    existing_start = None
    for index in range(dashboards_start + 1, dashboards_end):
        if _line_indent(lines[index]) == 4 and lines[index].strip() == key_line:
            existing_start = index
            break

    if existing_start is None:
        lines[dashboards_end:dashboards_end] = entry
    else:
        existing_end = dashboards_end
        for index in range(existing_start + 1, dashboards_end):
            stripped = lines[index].strip()
            if stripped and not stripped.startswith("#") and _line_indent(lines[index]) <= 4:
                existing_end = index
                break
        lines[existing_start:existing_end] = entry

    return _write_if_changed(path, source, lines, dashboard_key, filename)


def _write_if_changed(
    path: Path, original: str, lines: list[str], dashboard_key: str, filename: str
) -> ConfigPatchResult:
    updated = "".join(lines)
    if updated == original:
        return ConfigPatchResult(False, None, dashboard_key, filename)

    path.parent.mkdir(parents=True, exist_ok=True)
    backup_path = None
    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = path.with_name(f"{path.name}.{timestamp}.bak")
        shutil.copy2(path, backup)
        backup_path = str(backup)

    path.write_text(updated, encoding="utf-8")
    return ConfigPatchResult(True, backup_path, dashboard_key, filename)
