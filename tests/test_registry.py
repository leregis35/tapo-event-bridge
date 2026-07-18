"""Tests for the in-memory camera registry."""

from custom_components.tapo_event_bridge.models import CameraDiagnostic
from custom_components.tapo_event_bridge.registry import CameraRegistry


def test_registry_replaces_and_sorts_cameras() -> None:
    registry = CameraRegistry()
    registry.replace(
        [
            CameraDiagnostic(identifier="camera-b"),
            CameraDiagnostic(identifier="camera-a"),
        ]
    )

    assert len(registry) == 2
    assert [camera.identifier for camera in registry.values()] == [
        "camera-a",
        "camera-b",
    ]


def test_registry_replace_is_atomic() -> None:
    registry = CameraRegistry()
    registry.replace([CameraDiagnostic(identifier="camera-a")])
    registry.replace([CameraDiagnostic(identifier="camera-b")])

    assert registry.get("camera-a") is None
    assert registry.get("camera-b") is not None
