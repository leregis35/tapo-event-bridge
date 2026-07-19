import asyncio

import pytest

from custom_components.tapo_event_bridge.event_engine import EventEngine, EventRecorder
from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventType,
)


def make_event(camera_id: str, event_type: EventType) -> CameraEvent:
    return CameraEvent(
        camera_id=camera_id,
        event_type=event_type,
        source=EventSource.TEST,
    )


def test_recorder_is_bounded() -> None:
    recorder = EventRecorder(max_events=2)
    first = make_event("garage", EventType.MOTION)
    second = make_event("garage", EventType.PERSON)
    third = make_event("carport", EventType.VEHICLE)

    recorder.record(first)
    recorder.record(second)
    recorder.record(third)

    assert recorder.snapshot() == (second, third)


def test_recorder_filters_and_limits() -> None:
    recorder = EventRecorder(max_events=10)
    events = (
        make_event("garage", EventType.MOTION),
        make_event("garage", EventType.PERSON),
        make_event("carport", EventType.PERSON),
    )
    for event in events:
        recorder.record(event)

    assert recorder.snapshot(camera_id="garage") == events[:2]
    assert recorder.snapshot(event_type=EventType.PERSON) == events[1:]
    assert recorder.snapshot(limit=1) == (events[-1],)


def test_recorder_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        EventRecorder(max_events=0)

    recorder = EventRecorder()
    with pytest.raises(ValueError, match="negative"):
        recorder.snapshot(limit=-1)


def test_engine_dispatches_sync_and_async_subscribers() -> None:
    engine = EventEngine()
    received: list[str] = []

    def sync_callback(event: CameraEvent) -> None:
        received.append(f"sync:{event.event_type}")

    async def async_callback(event: CameraEvent) -> None:
        await asyncio.sleep(0)
        received.append(f"async:{event.event_type}")

    engine.subscribe(sync_callback)
    engine.subscribe(async_callback)

    asyncio.run(engine.publish(make_event("garage", EventType.PERSON)))

    assert received == ["sync:person", "async:person"]
    assert len(engine.recorder) == 1


def test_unsubscribe_is_idempotent() -> None:
    engine = EventEngine()
    received: list[CameraEvent] = []
    unsubscribe = engine.subscribe(received.append)

    unsubscribe()
    unsubscribe()
    asyncio.run(engine.publish(make_event("garage", EventType.MOTION)))

    assert received == []


def test_replay_publishes_copies_without_raw_payload() -> None:
    engine = EventEngine()
    original = CameraEvent(
        camera_id="garage",
        event_type=EventType.PERSON,
        source=EventSource.LOCAL,
        raw_payload={"private": True},
    )
    asyncio.run(engine.publish(original))

    replayed = asyncio.run(engine.replay(limit=1))

    assert len(replayed) == 1
    assert replayed[0].source is EventSource.REPLAY
    assert replayed[0].raw_payload is None
    assert len(engine.recorder) == 2


def test_diagnostic_snapshot_expands_in_developer_mode() -> None:
    engine = EventEngine(recorder=EventRecorder(max_events=30))
    for index in range(10):
        asyncio.run(engine.publish(make_event(f"camera-{index}", EventType.MOTION)))

    assert len(engine.diagnostic_snapshot()["recent_events"]) == 5

    engine.developer_mode = True
    assert len(engine.diagnostic_snapshot()["recent_events"]) == 10


def test_engine_suppresses_short_window_duplicates() -> None:
    engine = EventEngine(duplicate_window_seconds=1.0)
    first = make_event("garage", EventType.MOTION)
    duplicate = CameraEvent(
        camera_id=first.camera_id,
        event_type=first.event_type,
        source=first.source,
        state=first.state,
        occurred_at=first.occurred_at,
        received_at=first.received_at,
    )

    assert asyncio.run(engine.publish(first)) is True
    assert asyncio.run(engine.publish(duplicate)) is False
    assert len(engine.recorder) == 1
    assert engine.duplicate_count == 1


def test_replay_bypasses_duplicate_suppression() -> None:
    engine = EventEngine(duplicate_window_seconds=60.0)
    asyncio.run(engine.publish(make_event("garage", EventType.PERSON)))

    replayed = asyncio.run(engine.replay(limit=1))

    assert len(replayed) == 1
    assert len(engine.recorder) == 2


def test_clear_resets_history_and_signature_cache() -> None:
    engine = EventEngine()
    event = make_event("garage", EventType.MOTION)
    asyncio.run(engine.publish(event))

    engine.clear()

    assert len(engine.recorder) == 0
    assert asyncio.run(engine.publish(event)) is True
