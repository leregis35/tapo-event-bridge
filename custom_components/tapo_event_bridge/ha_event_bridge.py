"""Bridge existing Home Assistant camera entities into normalized events."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .discovery import privacy_safe_identifier
from .events import CameraEvent, EventSource, EventState, EventType

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .runtime import TapoEventBridgeRuntime


_EVENT_TOKEN_MAP: tuple[tuple[tuple[str, ...], EventType], ...] = (
    (("line_crossing", "line crossing"), EventType.LINE_CROSSING),
    (("intrusion",), EventType.INTRUSION),
    (("tamper", "sabotage"), EventType.TAMPER),
    (("crying", "baby_cry", "baby cry", "pleurs"), EventType.CRYING),
    (("vehicle", "car", "voiture", "véhicule"), EventType.VEHICLE),
    (("animal", "pet", "animaux"), EventType.ANIMAL),
    (("person", "human", "personne"), EventType.PERSON),
    (("motion", "occupancy", "presence", "mouvement"), EventType.MOTION),
)


def classify_event_type(
    entity_id: str,
    attributes: Mapping[str, Any] | None = None,
) -> EventType:
    """Classify one HA entity using only observable registry/state metadata."""
    attributes = attributes or {}
    searchable = " ".join(
        str(value).casefold()
        for value in (
            entity_id,
            attributes.get("device_class", ""),
            attributes.get("friendly_name", ""),
        )
    )
    for tokens, event_type in _EVENT_TOKEN_MAP:
        if any(token in searchable for token in tokens):
            return event_type
    return EventType.UNKNOWN


def event_state_from_ha_state(new_state: str) -> EventState:
    """Translate a Home Assistant state into an event lifecycle state."""
    normalized = new_state.casefold()
    if normalized in {"on", "open", "detected", "active"}:
        return EventState.STARTED
    if normalized in {"off", "closed", "clear", "inactive"}:
        return EventState.ENDED
    return EventState.INSTANT


def build_event_from_state_change(
    *,
    camera_id: str,
    entity_id: str,
    old_state: str | None,
    new_state: str,
    attributes: Mapping[str, Any] | None = None,
    occurred_at: datetime | None = None,
    camera_name: str | None = None,
    camera_model: str | None = None,
) -> CameraEvent | None:
    """Create a normalized event for a meaningful HA state transition."""
    if old_state == new_state:
        return None

    domain = entity_id.split(".", 1)[0]
    if domain == "camera":
        if new_state == "unavailable":
            event_type = EventType.CAMERA_OFFLINE
        elif old_state == "unavailable" and new_state != "unavailable":
            event_type = EventType.CAMERA_ONLINE
        else:
            return None
        state = EventState.INSTANT
    elif domain == "binary_sensor":
        event_type = classify_event_type(entity_id, attributes)
        if event_type is EventType.UNKNOWN:
            return None
        state = event_state_from_ha_state(new_state)
    else:
        return None

    safe_entity = privacy_safe_identifier(entity_id)
    return CameraEvent(
        camera_id=camera_id,
        event_type=event_type,
        source=EventSource.HOME_ASSISTANT,
        state=state,
        occurred_at=occurred_at or datetime.now(UTC),
        metadata={
            "source_entity": safe_entity,
            "source_entity_id": entity_id,
            "source_domain": domain,
            "camera_name": camera_name,
            "camera_model": camera_model,
            "previous_state": old_state,
            "new_state": new_state,
            "evidence": "observed",
        },
    )


async def async_subscribe_home_assistant_events(
    hass: HomeAssistant,
    runtime: TapoEventBridgeRuntime,
) -> Callable[[], None]:
    """Subscribe only to relevant camera entities, with no global polling."""
    from homeassistant.core import Event, EventStateChangedData, callback
    from homeassistant.helpers import entity_registry as er
    from homeassistant.helpers.event import async_track_state_change_event

    entity_registry = er.async_get(hass)
    camera_ids = set(runtime.cameras)
    tracked: dict[str, tuple[str, str | None, str | None]] = {}

    for entity in entity_registry.entities.values():
        if entity.disabled or entity.device_id is None:
            continue
        domain = entity.entity_id.split(".", 1)[0]
        if domain not in {"binary_sensor", "camera"}:
            continue
        camera_id = privacy_safe_identifier(entity.device_id)
        if camera_id in camera_ids:
            camera = runtime.cameras[camera_id]
            tracked[entity.entity_id] = (
                camera_id,
                camera.name,
                None if camera.model.value is None else str(camera.model.value),
            )

    if not tracked:
        return lambda: None

    @callback
    def _async_state_changed(event: Event[EventStateChangedData]) -> None:
        entity_id = event.data["entity_id"]
        source = tracked.get(entity_id)
        new_state = event.data["new_state"]
        old_state = event.data["old_state"]
        if source is None or new_state is None:
            return
        camera_id, camera_name, camera_model = source

        normalized = build_event_from_state_change(
            camera_id=camera_id,
            entity_id=entity_id,
            old_state=None if old_state is None else old_state.state,
            new_state=new_state.state,
            attributes=new_state.attributes,
            occurred_at=new_state.last_changed,
            camera_name=camera_name,
            camera_model=camera_model,
        )
        if normalized is not None:
            hass.async_create_task(runtime.publish_event(normalized))

    runtime.transports.append(EventSource.HOME_ASSISTANT.value)
    return async_track_state_change_event(hass, tuple(tracked), _async_state_changed)
