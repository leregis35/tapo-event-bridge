from datetime import UTC, datetime

import pytest

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventState,
    EventType,
)
from custom_components.tapo_event_bridge.models import DiscoveredEntity
from custom_components.tapo_event_bridge.person_lighting import (
    build_person_light_targets,
    should_trigger_person_lighting,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _event(
    event_type: EventType = EventType.PERSON,
    state: EventState = EventState.STARTED,
    source: EventSource = EventSource.HOME_ASSISTANT,
) -> CameraEvent:
    now = datetime.now(UTC)
    return CameraEvent(
        camera_id="camera-one",
        event_type=event_type,
        state=state,
        source=source,
        occurred_at=now,
        received_at=now,
    )


def test_person_lighting_only_accepts_live_person_start_events() -> None:
    assert should_trigger_person_lighting(_event())
    assert should_trigger_person_lighting(_event(state=EventState.INSTANT))
    assert not should_trigger_person_lighting(_event(state=EventState.ENDED))
    assert not should_trigger_person_lighting(_event(event_type=EventType.MOTION))
    assert not should_trigger_person_lighting(_event(source=EventSource.REPLAY))


def test_build_person_light_targets_uses_enabled_same_device_lights() -> None:
    entities = (
        DiscoveredEntity("light.carport_floodlight_timed", "tapo", "dev-1"),
        DiscoveredEntity("binary_sensor.carport_person", "tapo", "dev-1"),
        DiscoveredEntity("light.disabled", "tapo", "dev-1", disabled=True),
        DiscoveredEntity("light.other", "tapo", "dev-2"),
    )
    assert build_person_light_targets({"dev-1": "camera-one"}, entities) == {
        "camera-one": ("light.carport_floodlight_timed",)
    }


def test_runtime_person_lighting_configuration_and_status() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.person_light_targets = {
        "camera-one": ("light.carport_floodlight_timed",)
    }
    runtime.set_person_lighting_enabled(True)
    runtime.set_person_lighting_duration(90)
    runtime.note_person_lighting_trigger(
        _event(), ("light.carport_floodlight_timed",)
    )

    status = runtime.person_lighting_status
    assert status["enabled"] is True
    assert status["duration_seconds"] == 90
    assert status["mapped_camera_count"] == 1
    assert status["mapped_light_count"] == 1
    assert status["trigger_count"] == 1


def test_person_lighting_duration_is_bounded() -> None:
    runtime = TapoEventBridgeRuntime()
    with pytest.raises(ValueError):
        runtime.set_person_lighting_duration(9)
    with pytest.raises(ValueError):
        runtime.set_person_lighting_duration(901)
