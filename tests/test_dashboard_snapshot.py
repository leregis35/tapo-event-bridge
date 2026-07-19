import asyncio

from custom_components.tapo_event_bridge.events import (
    CameraEvent,
    EventSource,
    EventState,
    EventType,
)
from custom_components.tapo_event_bridge.models import (
    CameraDiagnostic,
    DiagnosticFact,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _camera() -> CameraDiagnostic:
    return CameraDiagnostic(
        identifier="garage",
        name="Garage",
        model=DiagnosticFact(value="C520WS"),
        capabilities={"motion": DiagnosticFact(value=True)},
        entity_count=3,
        enabled_entity_count=3,
    )


def test_dashboard_snapshot_has_stable_compact_schema() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery((_camera(),))

    snapshot = runtime.dashboard_snapshot

    assert snapshot["schema_version"] == 1
    assert snapshot["camera_count"] == 1
    assert snapshot["cameras"][0]["identifier"] == "garage"
    assert snapshot["cameras"][0]["capabilities"] == ["motion"]
    assert "data_policy" in snapshot


def test_dashboard_snapshot_reflects_event_activity() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery((_camera(),))

    async def publish() -> None:
        await runtime.publish_event(
            CameraEvent(
                camera_id="garage",
                event_type=EventType.MOTION,
                source=EventSource.HOME_ASSISTANT,
                state=EventState.STARTED,
            )
        )

    asyncio.run(publish())
    snapshot = runtime.dashboard_snapshot

    assert snapshot["recorded_event_count"] == 1
    assert snapshot["active_event_count"] == 1
    assert snapshot["event_types"] == {"motion": 1}
    assert snapshot["cameras"][0]["active_events"] == ["motion"]
