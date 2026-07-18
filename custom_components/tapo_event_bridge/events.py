"""Normalized camera-event models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any
from uuid import uuid4


class EventType(StrEnum):
    """Normalized event types understood by the bridge."""

    MOTION = "motion"
    PERSON = "person"
    VEHICLE = "vehicle"
    ANIMAL = "animal"
    CRYING = "crying"
    TAMPER = "tamper"
    LINE_CROSSING = "line_crossing"
    INTRUSION = "intrusion"
    CAMERA_ONLINE = "camera_online"
    CAMERA_OFFLINE = "camera_offline"
    UNKNOWN = "unknown"


class EventState(StrEnum):
    """Lifecycle state for an event."""

    STARTED = "started"
    UPDATED = "updated"
    ENDED = "ended"
    INSTANT = "instant"


class EventSource(StrEnum):
    """Transport or mechanism that produced an event."""

    LOCAL = "local"
    ONVIF = "onvif"
    RTSP = "rtsp"
    CLOUD = "cloud"
    HOME_ASSISTANT = "home_assistant"
    REPLAY = "replay"
    TEST = "test"
    UNKNOWN = "unknown"


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _validate_timestamp(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        msg = f"{field_name} must be timezone-aware"
        raise ValueError(msg)


@dataclass(slots=True, frozen=True)
class CameraEvent:
    """Transport-neutral event emitted by a camera."""

    camera_id: str
    event_type: EventType
    source: EventSource
    state: EventState = EventState.INSTANT
    occurred_at: datetime = field(default_factory=_utc_now)
    received_at: datetime = field(default_factory=_utc_now)
    confidence: float | None = None
    event_id: str = field(default_factory=lambda: uuid4().hex)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    raw_payload: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate and freeze mutable inputs."""
        if not self.camera_id.strip():
            raise ValueError("camera_id must not be empty")
        if not self.event_id.strip():
            raise ValueError("event_id must not be empty")
        _validate_timestamp(self.occurred_at, "occurred_at")
        _validate_timestamp(self.received_at, "received_at")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def latency_ms(self) -> float:
        """Return transport latency in milliseconds, never below zero."""
        latency = (self.received_at - self.occurred_at).total_seconds() * 1000
        return max(0.0, latency)

    def as_dict(self, *, include_raw_payload: bool = False) -> dict[str, Any]:
        """Return a JSON-safe, privacy-conscious representation."""
        data: dict[str, Any] = {
            "camera_id": self.camera_id,
            "event_type": self.event_type.value,
            "source": self.source.value,
            "state": self.state.value,
            "occurred_at": self.occurred_at.isoformat(),
            "received_at": self.received_at.isoformat(),
            "confidence": self.confidence,
            "event_id": self.event_id,
            "metadata": dict(self.metadata),
            "latency_ms": round(self.latency_ms, 3),
        }
        if include_raw_payload:
            data["raw_payload"] = self.raw_payload
        return data

    def as_replay(self, *, received_at: datetime | None = None) -> CameraEvent:
        """Create a replay copy without mutating the original event."""
        replay_metadata = dict(self.metadata)
        replay_metadata["replayed_from"] = self.event_id
        return replace(
            self,
            source=EventSource.REPLAY,
            received_at=received_at or _utc_now(),
            event_id=uuid4().hex,
            metadata=replay_metadata,
            raw_payload=None,
        )
