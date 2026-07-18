import asyncio

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventType,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def test_runtime_publishes_event_and_updates_status() -> None:
    runtime = TapoEventBridgeRuntime()
    event = CameraEvent(
        camera_id="garage",
        event_type=EventType.PERSON,
        source=EventSource.TEST,
    )

    asyncio.run(runtime.publish_event(event))

    assert runtime.status == "event_ready"
    assert runtime.event_engine.recorder.snapshot() == (event,)
