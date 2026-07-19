"""Regression tests for Recorder-safe Capability Explorer attributes."""

from __future__ import annotations

import json

from custom_components.tapo_event_bridge.attributes import (
    build_capability_explorer_attributes,
)
from custom_components.tapo_event_bridge.models import (
    CameraDiagnostic,
    DiagnosticFact,
    EvidenceLevel,
)
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def _camera(index: int, capability_count: int = 48) -> CameraDiagnostic:
    return CameraDiagnostic(
        identifier=f"camera-{index:02d}",
        name=f"Camera {index:02d}",
        model=DiagnosticFact(
            value="C520WS",
            evidence=EvidenceLevel.OBSERVED,
            source="registry",
        ),
        firmware=DiagnosticFact(value="1.2.3"),
        hardware_version=DiagnosticFact(value="1.0"),
        capabilities={
            f"capability_{number:02d}": DiagnosticFact(
                value=True,
                evidence=EvidenceLevel.OBSERVED,
                source="entity registry",
                note="Detailed evidence remains available in diagnostics.",
            )
            for number in range(capability_count)
        },
        entity_count=64,
        enabled_entity_count=60,
        disabled_entity_count=4,
        source_platforms=("tapo_control", "onvif"),
    )


def test_recorder_summary_omits_verbose_evidence() -> None:
    summary = _camera(1).recorder_summary()

    assert summary["model"] == "C520WS"
    assert isinstance(summary["capabilities"], list)
    assert summary["capabilities_truncated"] is True
    assert "evidence" not in json.dumps(summary)


def test_capability_explorer_attributes_stay_under_recorder_limit() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.complete_discovery(tuple(_camera(index) for index in range(20)))
    attributes = build_capability_explorer_attributes(runtime)
    payload_size = len(json.dumps(attributes, separators=(",", ":")).encode())

    assert payload_size < 16_384
    assert len(attributes["cameras"]) == 12
    assert attributes["cameras_truncated"] is True
    assert "Full evidence" in attributes["storage_policy"]
