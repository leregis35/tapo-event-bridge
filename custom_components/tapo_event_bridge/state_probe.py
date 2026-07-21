"""Opt-in Home Assistant state-change probe for camera diagnostics."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .discovery import privacy_safe_identifier

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .runtime import TapoEventBridgeRuntime

_SAFE_ATTRIBUTE_KEYS = (
    "device_class",
    "friendly_name",
    "unit_of_measurement",
)


def build_probe_entry(
    *,
    camera_id: str,
    camera_name: str | None,
    entity_id: str,
    old_state: str | None,
    new_state: str,
    attributes: Mapping[str, Any] | None = None,
    changed_at: datetime | None = None,
) -> dict[str, object] | None:
    """Build one bounded diagnostic entry for a meaningful state change."""
    if old_state == new_state:
        return None
    attributes = attributes or {}
    selected_attributes = {
        key: attributes[key]
        for key in _SAFE_ATTRIBUTE_KEYS
        if key in attributes and isinstance(attributes[key], (str, int, float, bool))
    }
    return {
        "time": (changed_at or datetime.now(UTC)).isoformat(),
        "camera_id": camera_id,
        "camera_name": camera_name,
        "entity_id": entity_id,
        "safe_entity": privacy_safe_identifier(entity_id),
        "domain": entity_id.split(".", 1)[0],
        "old_state": old_state,
        "new_state": new_state,
        "attributes": selected_attributes,
    }


async def async_subscribe_state_probe(
    hass: HomeAssistant,
    runtime: TapoEventBridgeRuntime,
) -> Callable[[], None]:
    """Track HA entity changes for discovered cameras while probe mode is armed."""
    from homeassistant.core import Event, EventStateChangedData, callback
    from homeassistant.helpers import entity_registry as er
    from homeassistant.helpers.event import async_track_state_change_event

    entity_registry = er.async_get(hass)
    known_camera_ids = set(runtime.cameras)
    tracked: dict[str, tuple[str, str | None]] = {}

    for entity in entity_registry.entities.values():
        if entity.disabled or entity.device_id is None:
            continue
        camera_id = privacy_safe_identifier(entity.device_id)
        if camera_id not in known_camera_ids:
            continue
        camera = runtime.cameras[camera_id]
        tracked[entity.entity_id] = (camera_id, camera.name)

    runtime.set_state_probe_tracked_entity_count(len(tracked))
    if not tracked:
        return lambda: None

    @callback
    def _async_state_changed(event: Event[EventStateChangedData]) -> None:
        if not runtime.state_probe_enabled:
            return
        entity_id = event.data["entity_id"]
        source = tracked.get(entity_id)
        new_state = event.data["new_state"]
        old_state = event.data["old_state"]
        if source is None or new_state is None:
            return
        camera_id, camera_name = source
        entry = build_probe_entry(
            camera_id=camera_id,
            camera_name=camera_name,
            entity_id=entity_id,
            old_state=None if old_state is None else old_state.state,
            new_state=new_state.state,
            attributes=new_state.attributes,
            changed_at=new_state.last_changed,
        )
        if entry is not None:
            runtime.add_state_probe_entry(entry)

    return async_track_state_change_event(hass, tuple(tracked), _async_state_changed)
