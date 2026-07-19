from custom_components.tapo_event_bridge.models import (
    CameraDiagnostic,
    DiagnosticFact,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _camera(
    identifier: str,
    model: str | None,
    power: str,
    capabilities: tuple[str, ...],
) -> CameraDiagnostic:
    return CameraDiagnostic(
        identifier=identifier,
        name=identifier.title(),
        model=DiagnosticFact(value=model),
        battery_powered=DiagnosticFact(value=power == "battery"),
        solar_powered=DiagnosticFact(value=power == "solar"),
        capabilities={name: DiagnosticFact(value=True) for name in capabilities},
        entity_count=4,
        enabled_entity_count=4,
        entity_domains={"camera": 1, "sensor": 3},
        source_platforms=("tapo_control",),
    )


def test_fleet_insights_aggregates_registry_evidence() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery(
        (
            _camera("garage", "C520WS", "unknown", ("motion", "person")),
            _camera("entry", "C425", "battery", ("motion",)),
        )
    )

    insights = runtime.fleet_insights

    assert insights["camera_count"] == 2
    assert insights["model_distribution"] == {"C425": 1, "C520WS": 1}
    assert insights["power_distribution"] == {"battery": 1, "unknown": 1}
    assert insights["platform_distribution"] == {"tapo_control": 2}
    assert insights["entity_domain_distribution"] == {"camera": 2, "sensor": 6}
    assert insights["capability_coverage_percent"] == {"motion": 100, "person": 50}
    assert insights["grade"] in {"good", "excellent"}


def test_fleet_insights_flags_incomplete_camera_evidence() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery(
        (CameraDiagnostic(identifier="unknown-camera", name="Unknown"),)
    )

    insights = runtime.fleet_insights
    attention = insights["cameras_needing_attention"]

    assert insights["grade"] == "attention"
    assert attention[0]["identifier"] == "unknown-camera"
    assert "model_unknown" in attention[0]["reasons"]
    assert "no_entities" in attention[0]["reasons"]
    assert "no_observed_capabilities" in attention[0]["reasons"]


def test_fleet_insights_reports_empty_state() -> None:
    runtime = TapoEventBridgeRuntime()

    assert runtime.fleet_insights["grade"] == "empty"
    assert runtime.fleet_insights["camera_count"] == 0
