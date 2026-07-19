"""Tests for the diagnostic data model."""

from custom_components.tapo_event_bridge.models import (
    CameraDiagnostic,
    DiagnosticFact,
    EvidenceLevel,
)


def test_diagnostic_fact_serialization() -> None:
    fact = DiagnosticFact(
        value=True,
        evidence=EvidenceLevel.OBSERVED,
        source="garage walk test",
        note="Detection enabled in the Tapo app.",
    )
    assert fact.as_dict()["evidence"] == EvidenceLevel.OBSERVED


def test_camera_diagnostic_serialization() -> None:
    camera = CameraDiagnostic(
        identifier="camera-1",
        model=DiagnosticFact(
            value="C520WS",
            evidence=EvidenceLevel.CONFIRMED,
            source="device info",
        ),
        capabilities={
            "person_detection": DiagnosticFact(
                value=True,
                evidence=EvidenceLevel.OBSERVED,
                source="Tapo application",
            )
        },
    )
    report = camera.as_dict()
    assert report["model"]["value"] == "C520WS"
    assert report["capabilities"]["person_detection"]["value"] is True


def test_unknown_is_the_default_evidence_level() -> None:
    camera = CameraDiagnostic(identifier="camera-1")
    assert camera.rtsp.evidence is EvidenceLevel.UNKNOWN
    assert camera.cloud_api.evidence is EvidenceLevel.UNKNOWN
