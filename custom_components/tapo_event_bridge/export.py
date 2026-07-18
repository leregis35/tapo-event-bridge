"""Privacy-safe diagnostic export helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .runtime import TapoEventBridgeRuntime


def build_export_payload(runtime: TapoEventBridgeRuntime) -> dict[str, Any]:
    """Build a JSON-serializable, privacy-safe discovery report."""
    return {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": runtime.status,
        "health_score": runtime.health_score,
        "camera_count": len(runtime.cameras),
        "entity_count": runtime.entity_count,
        "capability_count": runtime.capability_count,
        "last_discovery_at": (
            None
            if runtime.last_discovery_at is None
            else runtime.last_discovery_at.isoformat()
        ),
        "last_discovery_duration_ms": runtime.last_discovery_duration_ms,
        "last_discovery_error": runtime.last_discovery_error,
        "transports": list(runtime.transports),
        "cameras": {
            identifier: camera.as_dict()
            for identifier, camera in sorted(runtime.cameras.items())
        },
    }
