"""In-memory camera registry."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from .models import CameraDiagnostic


class CameraRegistry:
    """Small deterministic registry for discovered cameras."""

    def __init__(self) -> None:
        self._cameras: dict[str, CameraDiagnostic] = {}

    def replace(self, cameras: Iterable[CameraDiagnostic]) -> None:
        """Atomically replace the registry contents."""
        self._cameras = {camera.identifier: camera for camera in cameras}

    def get(self, identifier: str) -> CameraDiagnostic | None:
        """Return a camera by privacy-safe identifier."""
        return self._cameras.get(identifier)

    def values(self) -> tuple[CameraDiagnostic, ...]:
        """Return a stable snapshot sorted by identifier."""
        return tuple(self._cameras[key] for key in sorted(self._cameras))

    def as_dict(self) -> dict[str, CameraDiagnostic]:
        """Return a shallow copy for runtime compatibility."""
        return dict(self._cameras)

    def __len__(self) -> int:
        return len(self._cameras)

    def __iter__(self) -> Iterator[CameraDiagnostic]:
        return iter(self.values())
