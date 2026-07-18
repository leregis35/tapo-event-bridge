"""Tests for privacy-safe diagnostic export."""

from custom_components.tapo_event_bridge.export import build_export_payload
from custom_components.tapo_event_bridge.models import CameraDiagnostic
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
