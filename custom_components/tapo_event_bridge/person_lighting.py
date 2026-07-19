"""Person-detection lighting bridge using existing Home Assistant entities."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any

from .discovery import privacy_safe_identifier
from .events import CameraEvent, EventSource, EventState, EventType
from .models import DiscoveredEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .runtime import TapoEventBridgeRuntime


_LIGHT_HINTS = {"floodlight", "spotlight", "projecteur", "led", "light"}
_IGNORED_TOKENS = {
    "camera",
    "cam",
    "tapo",
    "tp",
    "link",
    "light",
    "floodlight",
    "spotlight",
    "projecteur",
    "timed",
    "led",
    "detection",
    "sensor",
    "binary",
}


def _tokens(value: str | None) -> set[str]:
    """Return accent-free meaningful matching tokens."""
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return {
        token
        for token in re.findall(r"[a-z0-9]+", ascii_value.casefold())
        if token not in _IGNORED_TOKENS and len(token) > 1
    }


def build_person_light_targets(
    camera_device_ids: dict[str, str],
    entities: Iterable[DiscoveredEntity],
    camera_names: Mapping[str, str | None] | None = None,
) -> dict[str, tuple[str, ...]]:
    """Map camera identifiers to enabled local or name-matched Tapo lights."""
    camera_names = camera_names or {}
    entity_list = tuple(entities)
    targets: dict[str, set[str]] = {}

    # Highest-confidence path: light and camera share the same HA device.
    for entity in entity_list:
        if entity.disabled or entity.device_id is None:
            continue
        if not entity.entity_id.startswith("light."):
            continue
        camera_id = camera_device_ids.get(entity.device_id)
        if camera_id is not None:
            targets.setdefault(camera_id, set()).add(entity.entity_id)

    # Fallback for integrations exposing the floodlight as a sibling device.
    for entity in entity_list:
        if entity.disabled or not entity.entity_id.startswith("light."):
            continue
        searchable = f"{entity.entity_id} {entity.original_name or ''}".casefold()
        if not any(hint in searchable for hint in _LIGHT_HINTS):
            continue
        light_tokens = _tokens(searchable)
        if not light_tokens:
            continue
        for camera_id, camera_name in camera_names.items():
            if targets.get(camera_id):
                continue
            camera_tokens = _tokens(camera_name)
            if camera_tokens and camera_tokens & light_tokens:
                targets.setdefault(camera_id, set()).add(entity.entity_id)

    return {
        camera_id: tuple(sorted(entity_ids))
        for camera_id, entity_ids in sorted(targets.items())
        if entity_ids
    }


def should_trigger_person_lighting(event: CameraEvent) -> bool:
    """Return whether an event should actuate person-detection lighting."""
    return (
        event.event_type is EventType.PERSON
        and event.state in {EventState.STARTED, EventState.INSTANT}
        and event.source is not EventSource.REPLAY
    )


async def async_discover_person_light_targets(
    hass: HomeAssistant,
    runtime: TapoEventBridgeRuntime,
) -> dict[str, tuple[str, ...]]:
    """Discover camera lights without contacting or waking any camera."""
    from homeassistant.helpers import entity_registry as er

    entity_registry = er.async_get(hass)
    known_camera_ids = set(runtime.cameras)
    device_to_camera: dict[str, str] = {}
    discovered: list[DiscoveredEntity] = []

    for entity in entity_registry.entities.values():
        if entity.device_id is not None:
            camera_id = privacy_safe_identifier(entity.device_id)
            if camera_id in known_camera_ids:
                device_to_camera[entity.device_id] = camera_id
        discovered.append(
            DiscoveredEntity(
                entity_id=entity.entity_id,
                platform=entity.platform,
                device_id=entity.device_id,
                original_name=entity.original_name,
                translation_key=entity.translation_key,
                disabled=entity.disabled,
            )
        )

    camera_names = {
        camera_id: camera.name for camera_id, camera in runtime.cameras.items()
    }
    return build_person_light_targets(
        device_to_camera,
        discovered,
        camera_names,
    )


async def async_setup_person_lighting(
    hass: HomeAssistant,
    runtime: TapoEventBridgeRuntime,
) -> Callable[[], None]:
    """Subscribe person events to mapped lights with a resettable timer."""
    from homeassistant.helpers.event import async_call_later

    runtime.person_light_targets = await async_discover_person_light_targets(
        hass, runtime
    )
    pending_off: dict[str, Callable[[], None]] = {}

    async def _turn_off(camera_id: str, _now: Any) -> None:
        pending_off.pop(camera_id, None)
        entity_ids = runtime.person_light_targets.get(camera_id, ())
        if entity_ids:
            await hass.services.async_call(
                "light",
                "turn_off",
                {"entity_id": list(entity_ids)},
                blocking=False,
            )

    async def _handle_event(event: CameraEvent) -> None:
        if not runtime.person_lighting_enabled:
            return
        if not should_trigger_person_lighting(event):
            return
        entity_ids = runtime.person_light_targets.get(event.camera_id, ())
        if not entity_ids:
            runtime.note_unmapped_person_event(event)
            return

        await hass.services.async_call(
            "light",
            "turn_on",
            {"entity_id": list(entity_ids)},
            blocking=False,
        )
        previous = pending_off.pop(event.camera_id, None)
        if previous is not None:
            previous()
        pending_off[event.camera_id] = async_call_later(
            hass,
            runtime.person_lighting_duration_seconds,
            lambda now: hass.async_create_task(_turn_off(event.camera_id, now)),
        )
        runtime.note_person_lighting_trigger(event, entity_ids)

    unsubscribe = runtime.event_engine.subscribe(_handle_event)

    def cleanup() -> None:
        unsubscribe()
        for cancel in tuple(pending_off.values()):
            cancel()
        pending_off.clear()

    return cleanup
