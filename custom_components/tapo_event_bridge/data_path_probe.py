"""Opt-in instrumentation of the observable Home Assistant camera data path."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .discovery import privacy_safe_identifier

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .runtime import TapoEventBridgeRuntime

_LOGGER = logging.getLogger(__package__)
_CANDIDATE_TOKENS = (
    "person", "people", "human", "motion", "occupancy", "presence",
    "alarm", "event", "trigger", "detect", "pir", "ring", "visitor",
)
_SAFE_ATTRIBUTE_KEYS = (
    "device_class", "friendly_name", "event_type", "type", "state",
    "status", "last_event", "last_alarm", "alarm_type", "detection_type",
)


def _safe_attributes(attributes: Mapping[str, Any]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in attributes.items():
        key_cf = str(key).casefold()
        is_candidate = key in _SAFE_ATTRIBUTE_KEYS or any(
            token in key_cf for token in _CANDIDATE_TOKENS
        )
        if is_candidate and (
            isinstance(value, (str, int, float, bool)) or value is None
        ):
            result[str(key)] = value
    return result


def build_data_path_entry(
    *,
    camera_id: str,
    camera_name: str | None,
    entity_id: str,
    old_state: str | None,
    new_state: str,
    old_attributes: Mapping[str, Any] | None,
    new_attributes: Mapping[str, Any] | None,
    changed_at: datetime | None = None,
) -> dict[str, object] | None:
    """Build one privacy-conscious state/attribute diff entry."""
    old_safe = _safe_attributes(old_attributes or {})
    new_safe = _safe_attributes(new_attributes or {})
    changed_attributes = {
        key: {"old": old_safe.get(key), "new": new_safe.get(key)}
        for key in sorted(set(old_safe) | set(new_safe))
        if old_safe.get(key) != new_safe.get(key)
    }
    if old_state == new_state and not changed_attributes:
        return None
    # Candidate matching deliberately excludes entity_id. Integration and entity
    # names often contain words such as "event" or "person", which created
    # false positives without any event-bearing value changing.
    searchable = " ".join(
        (str(new_state), str(new_safe), str(changed_attributes))
    ).casefold()
    candidate_tokens = sorted(
        {token for token in _CANDIDATE_TOKENS if token in searchable}
    )
    return {
        "time": (changed_at or datetime.now(UTC)).isoformat(),
        "camera_id": camera_id,
        "camera_name": camera_name,
        "entity_id": entity_id,
        "safe_entity": privacy_safe_identifier(entity_id),
        "domain": entity_id.split(".", 1)[0],
        "old_state": old_state,
        "new_state": new_state,
        "candidate_tokens": candidate_tokens,
        "changed_attributes": changed_attributes,
    }


async def async_subscribe_data_path_probe(
    hass: HomeAssistant,
    runtime: TapoEventBridgeRuntime,
) -> Callable[[], None]:
    """Observe updates for entities attached to discovered Tapo camera devices."""
    from homeassistant.core import Event, EventStateChangedData, callback
    from homeassistant.helpers import entity_registry as er
    from homeassistant.helpers.event import async_track_state_change_event

    registry = er.async_get(hass)
    known_camera_ids = set(runtime.cameras)
    tracked: dict[str, tuple[str, str | None]] = {}
    by_platform: dict[str, int] = {}
    for entity in registry.entities.values():
        if entity.disabled or entity.device_id is None:
            continue
        # The probe is about the camera integration data path, not every Home
        # Assistant device accidentally discovered by broad heuristics. Restrict
        # observation to entities actually provided by Tapo: Cameras Control.
        if entity.platform != "tapo_control":
            continue
        camera_id = privacy_safe_identifier(entity.device_id)
        if camera_id not in known_camera_ids:
            continue
        camera = runtime.cameras[camera_id]
        tracked[entity.entity_id] = (camera_id, camera.name)
        by_platform[entity.platform] = by_platform.get(entity.platform, 0) + 1

    runtime.set_data_path_tracked_entity_count(len(tracked))
    _LOGGER.info(
        "Data-path instrumentation ready: cameras=%d entities=%d platforms=%s",
        len(runtime.cameras), len(tracked), dict(sorted(by_platform.items())),
    )
    if not tracked:
        return lambda: None

    @callback
    def _async_state_changed(event: Event[EventStateChangedData]) -> None:
        if not runtime.data_path_probe_enabled:
            return
        entity_id = event.data["entity_id"]
        source = tracked.get(entity_id)
        new_state = event.data["new_state"]
        old_state = event.data["old_state"]
        if source is None or new_state is None:
            return
        camera_id, camera_name = source
        entry = build_data_path_entry(
            camera_id=camera_id,
            camera_name=camera_name,
            entity_id=entity_id,
            old_state=None if old_state is None else old_state.state,
            new_state=new_state.state,
            old_attributes={} if old_state is None else old_state.attributes,
            new_attributes=new_state.attributes,
            changed_at=new_state.last_updated,
        )
        if entry is None:
            return
        runtime.add_data_path_entry(entry)
        _LOGGER.debug("Camera data-path update: %s", entry)

    return async_track_state_change_event(hass, tuple(tracked), _async_state_changed)
