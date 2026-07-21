from datetime import UTC, datetime

from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime
from custom_components.tapo_event_bridge.state_probe import build_probe_entry


def test_build_probe_entry_keeps_exact_camera_and_entity() -> None:
    entry = build_probe_entry(
        camera_id="camera-1",
        camera_name="Carport",
        entity_id="select.carport_person_detection",
        old_state="off",
        new_state="on",
        attributes={"friendly_name": "Person Detection", "large": [1, 2, 3]},
        changed_at=datetime(2026, 7, 19, 21, 23, tzinfo=UTC),
    )
    assert entry is not None
    assert entry["camera_name"] == "Carport"
    assert entry["entity_id"] == "select.carport_person_detection"
    assert entry["domain"] == "select"
    assert entry["attributes"] == {"friendly_name": "Person Detection"}


def test_build_probe_entry_ignores_unchanged_state() -> None:
    assert build_probe_entry(
        camera_id="camera-1",
        camera_name="Carport",
        entity_id="sensor.carport_battery",
        old_state="90",
        new_state="90",
    ) is None


def test_runtime_probe_is_bounded_and_reported() -> None:
    runtime = TapoEventBridgeRuntime(state_probe_limit=2)
    runtime.set_state_probe_enabled(True)
    runtime.set_state_probe_tracked_entity_count(67)
    for index in range(3):
        runtime.add_state_probe_entry(
            {"camera_name": "Carport", "domain": "sensor", "index": index}
        )
    assert runtime.state_probe_state == "captured"
    assert len(runtime.state_probe_entries) == 2
    assert runtime.state_probe_report["tracked_entity_count"] == 67
    assert runtime.state_probe_report["captured_change_count"] == 2


def test_runtime_clear_probe_preserves_armed_state() -> None:
    runtime = TapoEventBridgeRuntime(state_probe_enabled=True)
    runtime.add_state_probe_entry({"camera_name": "Carport", "domain": "sensor"})
    runtime.clear_state_probe()
    assert runtime.state_probe_enabled is True
    assert runtime.state_probe_state == "armed"
