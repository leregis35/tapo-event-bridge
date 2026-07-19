import asyncio

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventState,
    EventType,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def test_event_activity_aggregates_and_tracks_active_events() -> None:
    runtime = TapoEventBridgeRuntime()

    async def publish() -> None:
        await runtime.publish_event(
            CameraEvent(
                camera_id="garage",
                event_type=EventType.MOTION,
                source=EventSource.HOME_ASSISTANT,
                state=EventState.STARTED,
            )
        )
        await runtime.publish_event(
            CameraEvent(
                camera_id="entry",
                event_type=EventType.PERSON,
                source=EventSource.HOME_ASSISTANT,
                state=EventState.STARTED,
            )
        )

    asyncio.run(publish())
    activity = runtime.event_activity

    assert activity["total"] == 2
    assert activity["by_type"] == {"motion": 1, "person": 1}
    assert activity["by_source"] == {"home_assistant": 2}
    assert activity["active_events"] == {
        "entry": ["person"],
        "garage": ["motion"],
    }


def test_event_activity_clears_ended_event() -> None:
    runtime = TapoEventBridgeRuntime()

    async def publish() -> None:
        for state in (EventState.STARTED, EventState.ENDED):
            await runtime.publish_event(
                CameraEvent(
                    camera_id="garage",
                    event_type=EventType.MOTION,
                    source=EventSource.HOME_ASSISTANT,
                    state=state,
                )
            )

    asyncio.run(publish())

    assert runtime.event_activity["active_events"] == {}
