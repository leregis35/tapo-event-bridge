from datetime import UTC, datetime, timedelta

import pytest

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventState,
    EventType,
)


def test_camera_event_serialization_hides_raw_payload() -> None:
    occurred_at = datetime(2026, 7, 18, 12, 0, tzinfo=UTC)
    event = CameraEvent(
        camera_id="garage",
        event_type=EventType.PERSON,
        source=EventSource.LOCAL,
        state=EventState.STARTED,
        occurred_at=occurred_at,
        received_at=occurred_at + timedelta(milliseconds=125),
        confidence=0.94,
        metadata={"zone": "driveway"},
        raw_payload={"secret": "not-exported"},
    )

    data = event.as_dict()

    assert data["event_type"] == "person"
    assert data["latency_ms"] == 125.0
    assert data["metadata"] == {"zone": "driveway"}
    assert "raw_payload" not in data


def test_camera_event_can_include_raw_payload_explicitly() -> None:
    event = CameraEvent(
        camera_id="garage",
        event_type=EventType.MOTION,
        source=EventSource.TEST,
        raw_payload={"detected": True},
    )

    assert event.as_dict(include_raw_payload=True)["raw_payload"] == {
        "detected": True
    }


def test_camera_event_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        CameraEvent(
            camera_id="garage",
            event_type=EventType.PERSON,
            source=EventSource.TEST,
            confidence=1.1,
        )


def test_camera_event_requires_timezone_aware_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        CameraEvent(
            camera_id="garage",
            event_type=EventType.PERSON,
            source=EventSource.TEST,
            occurred_at=datetime(2026, 7, 18, 12, 0),
        )


def test_replay_has_new_identity_and_no_raw_payload() -> None:
    original = CameraEvent(
        camera_id="garage",
        event_type=EventType.PERSON,
        source=EventSource.LOCAL,
        raw_payload={"private": True},
    )

    replay = original.as_replay()

    assert replay.event_id != original.event_id
    assert replay.source is EventSource.REPLAY
    assert replay.metadata["replayed_from"] == original.event_id
    assert replay.raw_payload is None
