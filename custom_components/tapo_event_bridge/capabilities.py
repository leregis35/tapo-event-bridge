"""Capability inference based only on Home Assistant registry evidence."""

from __future__ import annotations

from collections.abc import Iterable

from .models import DiagnosticFact, DiscoveredEntity, EvidenceLevel

_CAPABILITY_TOKENS: dict[str, tuple[str, ...]] = {
    "motion_detection": ("motion", "movement"),
    "person_detection": ("person", "human"),
    "vehicle_detection": ("vehicle", "car_detection"),
    "pet_detection": ("pet", "animal"),
    "crying_detection": ("cry", "baby_cry"),
    "sound_detection": ("sound", "audio_detection"),
    "tamper_detection": ("tamper",),
    "line_crossing_detection": ("line_cross", "linecross"),
    "area_intrusion_detection": ("intrusion", "area_detection"),
    "spotlight": ("spotlight", "floodlight", "lamp"),
    "siren": ("siren", "alarm_sound"),
    "privacy_mode": ("privacy",),
    "pan_tilt": ("pan", "tilt", "ptz"),
    "battery": ("battery",),
    "solar": ("solar", "panel"),
    "rtsp": ("rtsp",),
    "onvif": ("onvif",),
}


def _searchable_text(entity: DiscoveredEntity) -> str:
    """Return normalized registry text suitable for conservative matching."""
    values = (
        entity.entity_id,
        entity.original_name or "",
        entity.translation_key or "",
    )
    return " ".join(values).casefold().replace("-", "_").replace(" ", "_")


def infer_capabilities(
    entities: Iterable[DiscoveredEntity],
) -> dict[str, DiagnosticFact]:
    """Infer capabilities from entity-registry evidence without network calls."""
    matches: dict[str, list[str]] = {}

    for entity in entities:
        if entity.disabled:
            continue
        text = _searchable_text(entity)
        for capability, tokens in _CAPABILITY_TOKENS.items():
            if any(token in text for token in tokens):
                matches.setdefault(capability, []).append(entity.entity_id)

    return {
        capability: DiagnosticFact(
            value=True,
            evidence=EvidenceLevel.OBSERVED,
            source="Home Assistant entity registry",
            note=f"Exposed by: {', '.join(sorted(entity_ids))}",
        )
        for capability, entity_ids in sorted(matches.items())
    }


def capability_fact(
    capabilities: dict[str, DiagnosticFact],
    name: str,
) -> DiagnosticFact:
    """Return a capability fact, preserving unknown rather than guessing false."""
    return capabilities.get(name, DiagnosticFact())
