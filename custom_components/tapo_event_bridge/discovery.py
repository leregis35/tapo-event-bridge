"""Low-cost camera discovery from Home Assistant registries."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from hashlib import sha256
from typing import Any

from .capabilities import capability_fact, infer_capabilities
from .models import (
    CameraDiagnostic,
    DiagnosticFact,
    DiscoveredDevice,
    DiscoveredEntity,
    EvidenceLevel,
)

_TAPO_MANUFACTURER_MARKERS = ("tapo", "tp-link")
_TAPO_PLATFORM_MARKERS = ("tapo", "tapo_control")
_CAMERA_DOMAINS = {
    "binary_sensor",
    "button",
    "camera",
    "light",
    "select",
    "sensor",
    "switch",
}


def privacy_safe_identifier(device_id: str) -> str:
    """Return a stable identifier that does not expose Home Assistant IDs."""
    return f"camera-{sha256(device_id.encode()).hexdigest()[:12]}"


def _is_tapo_device(
    device: DiscoveredDevice,
    entities: Iterable[DiscoveredEntity],
) -> bool:
    manufacturer = (device.manufacturer or "").casefold()
    if any(marker in manufacturer for marker in _TAPO_MANUFACTURER_MARKERS):
        return True
    return any(
        any(marker in entity.platform.casefold() for marker in _TAPO_PLATFORM_MARKERS)
        for entity in entities
    )


def build_camera_diagnostics(
    devices: Iterable[DiscoveredDevice],
    entities: Iterable[DiscoveredEntity],
) -> tuple[CameraDiagnostic, ...]:
    """Build camera diagnostics without polling or waking any device."""
    entities_by_device: dict[str, list[DiscoveredEntity]] = defaultdict(list)
    for entity in entities:
        if entity.device_id is not None:
            entities_by_device[entity.device_id].append(entity)

    cameras: list[CameraDiagnostic] = []
    for device in devices:
        device_entities = entities_by_device.get(device.device_id, [])
        if not _is_tapo_device(device, device_entities):
            continue
        has_camera_entity = any(
            entity.entity_id.split(".", 1)[0] in _CAMERA_DOMAINS
            for entity in device_entities
        )
        if not has_camera_entity:
            continue

        capabilities = infer_capabilities(device_entities)
        platforms = tuple(sorted({entity.platform for entity in device_entities}))
        registry_source = "Home Assistant device registry"

        camera = CameraDiagnostic(
            identifier=privacy_safe_identifier(device.device_id),
            name=device.name_by_user or device.name,
            manufacturer=DiagnosticFact(
                value=device.manufacturer,
                evidence=EvidenceLevel.OBSERVED,
                source=registry_source,
            ),
            model=DiagnosticFact(
                value=device.model,
                evidence=EvidenceLevel.OBSERVED,
                source=registry_source,
            ),
            firmware=DiagnosticFact(
                value=device.sw_version,
                evidence=EvidenceLevel.OBSERVED,
                source=registry_source,
            ),
            hardware_version=DiagnosticFact(
                value=device.hw_version,
                evidence=EvidenceLevel.OBSERVED,
                source=registry_source,
            ),
            battery_powered=capability_fact(capabilities, "battery"),
            solar_powered=capability_fact(capabilities, "solar"),
            rtsp=capability_fact(capabilities, "rtsp"),
            onvif=capability_fact(capabilities, "onvif"),
            local_api=DiagnosticFact(
                value=True if platforms else None,
                evidence=(
                    EvidenceLevel.OBSERVED if platforms else EvidenceLevel.UNKNOWN
                ),
                source=("Home Assistant entity registry" if platforms else None),
                note=(
                    f"Observed platforms: {', '.join(platforms)}"
                    if platforms
                    else None
                ),
            ),
            capabilities=capabilities,
            entity_count=len(device_entities),
            source_platforms=platforms,
        )
        cameras.append(camera)

    return tuple(sorted(cameras, key=lambda camera: camera.identifier))


async def async_discover_cameras(hass: Any) -> tuple[CameraDiagnostic, ...]:
    """Read Home Assistant registries once and return discovered cameras."""
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    devices = tuple(
        DiscoveredDevice(
            device_id=device.id,
            name=device.name,
            name_by_user=device.name_by_user,
            manufacturer=device.manufacturer,
            model=device.model,
            sw_version=device.sw_version,
            hw_version=device.hw_version,
            config_entry_ids=frozenset(device.config_entries),
        )
        for device in device_registry.devices.values()
    )
    entities = tuple(
        DiscoveredEntity(
            entity_id=entity.entity_id,
            platform=entity.platform,
            device_id=entity.device_id,
            original_name=entity.original_name,
            translation_key=entity.translation_key,
            disabled=entity.disabled,
        )
        for entity in entity_registry.entities.values()
    )
    return build_camera_diagnostics(devices, entities)
