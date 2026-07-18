"""Normalized data models for Tapo Event Bridge."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class EvidenceLevel(StrEnum):
    """Confidence level assigned to a diagnostic fact."""

    CONFIRMED = "confirmed"
    OBSERVED = "observed"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class DiagnosticFact:
    """A value accompanied by its evidence level and source."""

    value: Any = None
    evidence: EvidenceLevel = EvidenceLevel.UNKNOWN
    source: str | None = None
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(slots=True, frozen=True)
class DiscoveredEntity:
    """Minimal entity-registry information used by discovery."""

    entity_id: str
    platform: str
    device_id: str | None
    original_name: str | None = None
    translation_key: str | None = None
    disabled: bool = False


@dataclass(slots=True, frozen=True)
class DiscoveredDevice:
    """Minimal device-registry information used by discovery."""

    device_id: str
    name: str | None = None
    name_by_user: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    sw_version: str | None = None
    hw_version: str | None = None
    config_entry_ids: frozenset[str] = frozenset()


@dataclass(slots=True)
class CameraDiagnostic:
    """Normalized diagnostic inventory for one camera."""

    identifier: str
    name: str | None = None
    manufacturer: DiagnosticFact = field(default_factory=DiagnosticFact)
    model: DiagnosticFact = field(default_factory=DiagnosticFact)
    firmware: DiagnosticFact = field(default_factory=DiagnosticFact)
    hardware_version: DiagnosticFact = field(default_factory=DiagnosticFact)
    battery_powered: DiagnosticFact = field(default_factory=DiagnosticFact)
    solar_powered: DiagnosticFact = field(default_factory=DiagnosticFact)
    local_api: DiagnosticFact = field(default_factory=DiagnosticFact)
    cloud_api: DiagnosticFact = field(default_factory=DiagnosticFact)
    rtsp: DiagnosticFact = field(default_factory=DiagnosticFact)
    onvif: DiagnosticFact = field(default_factory=DiagnosticFact)
    capabilities: dict[str, DiagnosticFact] = field(default_factory=dict)
    entity_count: int = 0
    source_platforms: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        data = asdict(self)
        data["capabilities"] = {
            name: fact.as_dict() for name, fact in self.capabilities.items()
        }
        return data
