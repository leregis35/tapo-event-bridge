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
    enabled_entity_count: int = 0
    disabled_entity_count: int = 0
    entity_domains: dict[str, int] = field(default_factory=dict)
    source_platforms: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        data = asdict(self)
        data["capabilities"] = {
            name: fact.as_dict() for name, fact in self.capabilities.items()
        }
        return data

    @property
    def power_source(self) -> str:
        """Return a conservative power-source label from observed evidence."""
        if self.solar_powered.value is True:
            return "solar"
        if self.battery_powered.value is True:
            return "battery"
        return "unknown"

    @property
    def health_score(self) -> int:
        """Return a registry-evidence completeness score for this camera."""
        score = 40
        if self.name:
            score += 10
        if self.model.value:
            score += 15
        if self.firmware.value:
            score += 10
        if self.entity_count:
            score += 15
        if self.capabilities:
            score += 10
        return min(score, 100)

    def capability_details(self) -> dict[str, dict[str, Any]]:
        """Return sorted capability evidence suitable for HA attributes."""
        return {
            name: fact.as_dict()
            for name, fact in sorted(self.capabilities.items())
        }

    def explorer_summary(self) -> dict[str, Any]:
        """Return the detailed, privacy-safe Capability Explorer profile."""
        return {
            "identifier": self.identifier,
            "name": self.name,
            "manufacturer": self.manufacturer.as_dict(),
            "model": self.model.as_dict(),
            "firmware": self.firmware.as_dict(),
            "hardware_version": self.hardware_version.as_dict(),
            "power_source": self.power_source,
            "battery_powered": self.battery_powered.as_dict(),
            "solar_powered": self.solar_powered.as_dict(),
            "local_api": self.local_api.as_dict(),
            "cloud_api": self.cloud_api.as_dict(),
            "rtsp": self.rtsp.as_dict(),
            "onvif": self.onvif.as_dict(),
            "health_score": self.health_score,
            "entity_count": self.entity_count,
            "enabled_entity_count": self.enabled_entity_count,
            "disabled_entity_count": self.disabled_entity_count,
            "entity_domains": dict(sorted(self.entity_domains.items())),
            "platforms": list(self.source_platforms),
            "capabilities": self.capability_details(),
        }

    def summary(self) -> dict[str, Any]:
        """Return a compact Home Assistant state-attribute representation."""
        return {
            "identifier": self.identifier,
            "name": self.name,
            "manufacturer": self.manufacturer.value,
            "model": self.model.value,
            "firmware": self.firmware.value,
            "power_source": self.power_source,
            "health_score": self.health_score,
            "entity_count": self.entity_count,
            "enabled_entity_count": self.enabled_entity_count,
            "disabled_entity_count": self.disabled_entity_count,
            "entity_domains": dict(sorted(self.entity_domains.items())),
            "platforms": list(self.source_platforms),
            "capabilities": sorted(self.capabilities),
        }
