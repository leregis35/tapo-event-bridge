from custom_components.tapo_event_bridge.models import CameraDiagnostic, DiagnosticFact
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _camera() -> CameraDiagnostic:
    return CameraDiagnostic(
        identifier="camera-safe",
        name="Garage",
        model=DiagnosticFact(value="C520WS"),
        capabilities={
            "motion_detection": DiagnosticFact(value=True),
            "spotlight": DiagnosticFact(value=True),
        },
        entity_count=8,
        enabled_entity_count=7,
        disabled_entity_count=1,
        entity_domains={"camera": 1, "sensor": 5, "light": 2},
        source_platforms=("tapo_control",),
    )


def test_runtime_inventory_totals_and_health() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.begin_discovery()
    runtime.complete_discovery((_camera(),))

    assert runtime.entity_count == 8
    assert runtime.capability_count == 2
    assert runtime.health_score == 100
    assert runtime.last_discovery_at is not None
    assert runtime.last_discovery_duration_ms is not None


def test_runtime_discovery_failure_is_visible() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.begin_discovery()
    runtime.fail_discovery(RuntimeError("boom"))

    assert runtime.status == "discovery_error"
    assert runtime.last_discovery_error == "RuntimeError"
    assert runtime.health_score == 25


def test_camera_summary_is_compact_and_sorted() -> None:
    summary = _camera().summary()

    assert summary["name"] == "Garage"
    assert summary["model"] == "C520WS"
    assert summary["capabilities"] == ["motion_detection", "spotlight"]
    assert summary["entity_domains"] == {"camera": 1, "light": 2, "sensor": 5}
