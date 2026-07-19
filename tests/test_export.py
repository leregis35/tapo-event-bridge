"""Tests for privacy-safe diagnostic export."""

from custom_components.tapo_event_bridge.export import build_export_payload
from custom_components.tapo_event_bridge.models import CameraDiagnostic, DiagnosticFact
from custom_components.tapo_event_bridge.runtime import TapoEventBridgeRuntime


def test_export_contains_discovery_snapshot() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.replace_cameras((CameraDiagnostic(identifier="camera-safe"),))

    payload = build_export_payload(runtime)

    assert payload["schema_version"] == 2
    assert payload["status"] == "discovery_ready"
    assert payload["camera_count"] == 1
    assert "camera-safe" in payload["cameras"]
    assert "generated_at" in payload


def test_export_keeps_full_capability_evidence() -> None:
    runtime = TapoEventBridgeRuntime()
    runtime.replace_cameras(
        (
            CameraDiagnostic(
                identifier="camera-safe",
                capabilities={
                    "motion": DiagnosticFact(
                        value=True,
                        source="entity registry",
                        note="Full evidence stays in diagnostics.",
                    )
                },
            ),
        )
    )

    payload = build_export_payload(runtime)
    fact = payload["cameras"]["camera-safe"]["capabilities"]["motion"]

    assert fact["value"] is True
    assert fact["source"] == "entity registry"
    assert fact["note"] == "Full evidence stays in diagnostics."
