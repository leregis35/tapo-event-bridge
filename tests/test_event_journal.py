import asyncio
import json
from datetime import UTC, datetime, timedelta

import pytest

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventState,
    EventType,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _event(
    camera_id: str,
    event_type: EventType,
    *,
    seconds: int,
) -> CameraEvent:
    occurred = datetime(2026, 7, 19, 12, 0, tzinfo=UTC) + timedelta(seconds=seconds)
    return CameraEvent(
        camera_id=camera_id,
        event_type=event_type,
        source=EventSource.HOME_ASSISTANT,
        state=EventState.STARTED,
        occurred_at=occurred,
        received_at=occurred,
    )


def test_event_journal_is_newest_first_and_filterable() -> None:
    runtime = TapoEventBridgeRuntime()

    async def publish() -> None:
        await runtime.publish_event(_event("garage", EventType.MOTION, seconds=1))
        await runtime.publish_event(_event("entry", EventType.PERSON, seconds=2))
        await runtime.publish_event(_event("garage", EventType.PERSON, seconds=3))

    asyncio.run(publish())

    journal = runtime.event_journal
    assert [item["camera_id"] for item in journal["events"]] == [
        "garage",
        "entry",
        "garage",
    ]

    runtime.set_journal_camera_filter("garage")
    runtime.set_journal_event_type_filter("person")
    filtered = runtime.event_journal
    assert filtered["matching_event_count"] == 1
    assert filtered["events"][0]["type"] == "person"


def test_event_journal_rejects_unknown_filters() -> None:
    runtime = TapoEventBridgeRuntime()
    with pytest.raises(ValueError, match="Unsupported camera filter"):
        runtime.set_journal_camera_filter("missing")
    with pytest.raises(ValueError, match="Unsupported event type filter"):
        runtime.set_journal_event_type_filter("missing")


def test_event_journal_is_recorder_safe() -> None:
    runtime = TapoEventBridgeRuntime(journal_limit=25)

    async def publish() -> None:
        for index in range(80):
            await runtime.publish_event(
                _event(
                    f"camera-{index % 6}",
                    EventType.PERSON if index % 2 else EventType.MOTION,
                    seconds=index * 2,
                )
            )

    asyncio.run(publish())
    payload = json.dumps(runtime.event_journal, separators=(",", ":"))
    assert runtime.event_journal["displayed_event_count"] == 25
    assert len(payload.encode()) < 16_384
