import asyncio
import json
from datetime import UTC, datetime, timedelta

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


def _camera(identifier: str, name: str) -> CameraDiagnostic:
    return CameraDiagnostic(
        identifier=identifier,
        name=name,
        model=DiagnosticFact(value="C520WS"),
        capabilities={"motion": DiagnosticFact(value=True)},
        entity_count=3,
        enabled_entity_count=3,
    )


def _event(
    camera_id: str,
    event_type: EventType,
    *,
    seconds: int,
    state: EventState = EventState.STARTED,
) -> CameraEvent:
    occurred = datetime(2026, 7, 19, 12, 0, tzinfo=UTC) + timedelta(seconds=seconds)
    return CameraEvent(
        camera_id=camera_id,
        event_type=event_type,
        source=EventSource.HOME_ASSISTANT,
        state=state,
        occurred_at=occurred,
        received_at=occurred,
    )


def test_fleet_overview_summarizes_live_camera_activity() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery(
        (_camera("garage", "Garage"), _camera("entry", "Entrée"))
    )

    async def publish() -> None:
        await runtime.publish_event(_event("garage", EventType.MOTION, seconds=1))
        await runtime.publish_event(_event("entry", EventType.PERSON, seconds=2))
        await runtime.publish_event(_event("garage", EventType.MOTION, seconds=3))

    asyncio.run(publish())
    overview = runtime.fleet_overview

    assert runtime.fleet_overview_state == "active"
    assert overview["camera_count"] == 2
    assert overview["recorded_event_count"] == 3
    assert overview["most_active_camera"] == {
        "identifier": "garage",
        "name": "Garage",
        "event_count": 2,
    }
    assert overview["last_event"]["camera_name"] == "Garage"
    garage = next(
        camera for camera in overview["cameras"] if camera["identifier"] == "garage"
    )
    assert garage["last_event_type"] == "motion"
    assert garage["active_events"] == ["motion"]


def test_fleet_overview_becomes_idle_when_activity_ends() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery((_camera("garage", "Garage"),))

    async def publish() -> None:
        await runtime.publish_event(_event("garage", EventType.MOTION, seconds=1))
        await runtime.publish_event(
            _event(
                "garage",
                EventType.MOTION,
                seconds=2,
                state=EventState.ENDED,
            )
        )

    asyncio.run(publish())

    assert runtime.fleet_overview_state == "idle"
    assert runtime.fleet_overview["active_event_count"] == 0


def test_fleet_overview_is_recorder_safe() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery(
        tuple(_camera(f"camera-{index}", f"Camera {index}") for index in range(20))
    )

    async def publish() -> None:
        for index in range(100):
            await runtime.publish_event(
                _event(
                    f"camera-{index % 20}",
                    EventType.PERSON if index % 2 else EventType.MOTION,
                    seconds=index,
                )
            )

    asyncio.run(publish())
    overview = runtime.fleet_overview
    payload = json.dumps(overview, separators=(",", ":"))

    assert len(overview["cameras"]) == 12
    assert overview["cameras_truncated"] is True
    assert len(payload.encode()) < 16_384
