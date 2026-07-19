"""Diagnostics support for Tapo Event Bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .export import build_export_payload

if TYPE_CHECKING:
    from . import TapoEventBridgeConfigEntry

TO_REDACT = {
    "access_token",
    "account_id",
    "api_key",
    "email",
    "host",
    "ip_address",
    "password",
    "refresh_token",
    "token",
    "username",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
) -> dict[str, Any]:
    """Return privacy-safe diagnostics for a config entry."""
    return {
        "config_entry": {
            "title": entry.title,
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "runtime": build_export_payload(entry.runtime_data),
        "event_engine": entry.runtime_data.event_engine.diagnostic_snapshot(),
        "evidence_legend": {
            "confirmed": (
                "Backed by documentation, protocol evidence, or a reproducible test."
            ),
            "observed": "Observed from Home Assistant or the camera lab.",
            "hypothesis": "Plausible but not yet proven.",
            "unknown": "Not tested or no reliable evidence available.",
        },
    }
