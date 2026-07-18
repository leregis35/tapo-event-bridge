"""Privacy-safe diagnostic export helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .runtime import TapoEventBridgeRuntime


def build_export_payload(runtime: TapoEventBridgeRuntime) -> dict[str, Any]:
    """Build a JSON-serializable, privacy-safe discovery report."""
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": runtime.status,
        "camera_count": len(runtime.cameras),
        "transports": list(runtime.transports),
        "cameras": {
            identifier: camera.as_dict()
            for identifier, camera in sorted(runtime.cameras.items())
        },
    }
