"""Diagnostics support for Tapo Event Bridge."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return safe diagnostics for a config entry."""
    return {
        "entry": {"title": entry.title, "version": entry.version},
        "integration": {
            "status": "foundation_ready",
            "event_transports": [],
            "discovered_devices": [],
        },
    }
