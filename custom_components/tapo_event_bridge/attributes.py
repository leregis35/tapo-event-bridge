"""Recorder-safe Home Assistant state attribute builders."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .runtime import TapoEventBridgeRuntime

MAX_RECORDER_EXPLORER_CAMERAS = 12
MAX_RECORDER_CAPABILITIES_PER_CAMERA = 32


def build_capability_explorer_attributes(
    runtime: TapoEventBridgeRuntime,
) -> dict[str, Any]:
    """Build compact Capability Explorer attributes safe for Recorder."""
    cameras = [
        camera.recorder_summary(
            max_capabilities=MAX_RECORDER_CAPABILITIES_PER_CAMERA
        )
        for _, camera in sorted(runtime.cameras.items())
    ]
    return {
        "camera_count": len(runtime.cameras),
        "entity_count": runtime.entity_count,
        "observed_capability_count": runtime.capability_count,
        "average_camera_health": runtime.average_camera_health,
        "last_scan": (
            None
            if runtime.last_discovery_at is None
            else runtime.last_discovery_at.isoformat()
        ),
        "scan_duration_ms": runtime.last_discovery_duration_ms,
        "last_error": runtime.last_discovery_error,
        "storage_policy": (
            "Compact Recorder-safe summary. Full evidence is available "
            "from Home Assistant diagnostics."
        ),
        "cameras": cameras[:MAX_RECORDER_EXPLORER_CAMERAS],
        "cameras_truncated": len(cameras) > MAX_RECORDER_EXPLORER_CAMERAS,
    }
