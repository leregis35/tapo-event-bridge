import asyncio

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventType,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def test_runtime_metrics_have_stable_production_fields() -> None:
    runtime = TapoEventBridgeRuntime()

    metrics = runtime.runtime_metrics

    assert metrics["uptime_seconds"] >= 0
    assert metrics["event_buffer_limit"] == 200
    assert metrics["suppressed_duplicate_count"] == 0
    assert "data_policy" in metrics


def test_clear_events_resets_the_bounded_history() -> None:
    runtime = TapoEventBridgeRuntime()
    asyncio.run(
        runtime.publish_event(
            CameraEvent(
                camera_id="garage",
                event_type=EventType.MOTION,
                source=EventSource.TEST,
            )
        )
    )
    assert runtime.recorded_event_count == 1

    runtime.clear_events()

    assert runtime.recorded_event_count == 0
