from custom_components.tapo_event_bridge.models import (
    CameraDiagnostic,
    DiagnosticFact,
    EvidenceLevel,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _camera() -> CameraDiagnostic:
    return CameraDiagnostic(
        identifier="camera-safe",
        name="Garage",
        model=DiagnosticFact(
            value="C520WS",
            evidence=EvidenceLevel.OBSERVED,
            source="registry",
        ),
        firmware=DiagnosticFact(value="1.2.3"),
        battery_powered=DiagnosticFact(value=True),
        capabilities={
            "motion_detection": DiagnosticFact(
                value=True,
                evidence=EvidenceLevel.OBSERVED,
                source="entity registry",
            )
        },
        entity_count=5,
        enabled_entity_count=4,
        disabled_entity_count=1,
        entity_domains={"camera": 1, "sensor": 4},
        source_platforms=("tapo_control",),
    )


def test_explorer_summary_preserves_evidence() -> None:
    profile = _camera().explorer_summary()

    assert profile["model"]["value"] == "C520WS"
    assert profile["model"]["evidence"] == "observed"
    assert profile["power_source"] == "battery"
    assert profile["capabilities"]["motion_detection"]["value"] is True


def test_camera_health_is_bounded() -> None:
    assert 0 <= _camera().health_score <= 100


def test_runtime_capability_explorer_states() -> None:
    runtime = TapoEventBridgeRuntime()
    assert runtime.capability_explorer_state == "no_cameras"

    runtime.begin_discovery()
    assert runtime.capability_explorer_state == "scanning"

    runtime.complete_discovery((_camera(),))
    assert runtime.capability_explorer_state == "ready"
    assert runtime.average_camera_health == _camera().health_score
