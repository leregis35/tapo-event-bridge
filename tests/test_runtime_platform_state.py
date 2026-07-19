"""Tests for runtime state consumed by Home Assistant platforms."""

import asyncio
from datetime import UTC, datetime, timedelta

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventType,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def test_runtime_notifies_and_unsubscribes_listeners() -> None:
    runtime = TapoEventBridgeRuntime()
    calls: list[str] = []
    unsubscribe = runtime.subscribe(lambda: calls.append(runtime.status))

    runtime.replace_cameras(())
    unsubscribe()
    runtime.replace_cameras(())

    assert calls == ["discovery_ready"]


def test_runtime_exposes_latest_event_and_count() -> None:
    runtime = TapoEventBridgeRuntime()
    occurred_at = datetime.now(UTC) - timedelta(milliseconds=25)
    event = CameraEvent(
        camera_id="garage",
        event_type=EventType.PERSON,
        source=EventSource.TEST,
        occurred_at=occurred_at,
    )

    asyncio.run(runtime.publish_event(event))

    assert runtime.latest_event is event
    assert runtime.recorded_event_count == 1
    assert runtime.status == "event_ready"


def test_replay_last_event_skips_existing_replays() -> None:
    runtime = TapoEventBridgeRuntime()
    original = CameraEvent(
        camera_id="garage",
        event_type=EventType.MOTION,
        source=EventSource.TEST,
    )

    async def run_replays() -> tuple[CameraEvent | None, CameraEvent | None]:
        await runtime.publish_event(original)
        first = await runtime.replay_last_event()
        second = await runtime.replay_last_event()
        return first, second

    first_replay, second_replay = asyncio.run(run_replays())

    assert first_replay is not None
    assert second_replay is not None
    assert first_replay.metadata["replayed_from"] == original.event_id
    assert second_replay.metadata["replayed_from"] == original.event_id
    assert runtime.recorded_event_count == 3


def test_runtime_close_runs_cleanup_once() -> None:
    runtime = TapoEventBridgeRuntime()
    calls: list[str] = []
    runtime.add_cleanup_callback(lambda: calls.append("closed"))

    runtime.close()
    runtime.close()

    assert calls == ["closed"]
