from custom_components.tapo_event_bridge.events import EventState, EventType
from custom_components.tapo_event_bridge.ha_event_bridge import (
    build_event_from_state_change,
    classify_event_type,
    event_state_from_ha_state,
)


def test_classifies_observed_detection_entities() -> None:
    assert (
        classify_event_type("binary_sensor.garage_person_detection") is EventType.PERSON
    )
    assert classify_event_type("binary_sensor.carport_vehicle") is EventType.VEHICLE
    assert classify_event_type("binary_sensor.salon_motion") is EventType.MOTION


def test_translates_binary_sensor_lifecycle() -> None:
    assert event_state_from_ha_state("on") is EventState.STARTED
    assert event_state_from_ha_state("off") is EventState.ENDED


def test_builds_privacy_safe_home_assistant_event() -> None:
    event = build_event_from_state_change(
        camera_id="camera-safe",
        entity_id="binary_sensor.garage_person_detection",
        old_state="off",
        new_state="on",
        attributes={"device_class": "motion"},
        camera_name="Garage",
        camera_model="C520WS",
    )

    assert event is not None
    assert event.camera_id == "camera-safe"
    assert event.event_type is EventType.PERSON
    assert event.state is EventState.STARTED
    assert event.metadata["source_entity"].startswith("camera-")
    assert "garage" not in str(event.metadata["source_entity"])
    assert event.metadata["source_entity_id"] == (
        "binary_sensor.garage_person_detection"
    )
    assert event.metadata["camera_name"] == "Garage"
    assert event.metadata["camera_model"] == "C520WS"


def test_ignores_unrelated_or_duplicate_state_changes() -> None:
    assert (
        build_event_from_state_change(
            camera_id="camera-safe",
            entity_id="sensor.garage_temperature",
            old_state="20",
            new_state="21",
        )
        is None
    )
    assert (
        build_event_from_state_change(
            camera_id="camera-safe",
            entity_id="binary_sensor.garage_motion",
            old_state="on",
            new_state="on",
        )
        is None
    )


def test_camera_availability_becomes_online_offline_events() -> None:
    offline = build_event_from_state_change(
        camera_id="camera-safe",
        entity_id="camera.garage",
        old_state="streaming",
        new_state="unavailable",
    )
    online = build_event_from_state_change(
        camera_id="camera-safe",
        entity_id="camera.garage",
        old_state="unavailable",
        new_state="idle",
    )

    assert offline is not None and offline.event_type is EventType.CAMERA_OFFLINE
    assert online is not None and online.event_type is EventType.CAMERA_ONLINE
