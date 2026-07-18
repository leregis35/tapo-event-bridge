"""Tests for conservative capability inference."""

from custom_components.tapo_event_bridge.capabilities import (
    capability_fact,
    infer_capabilities,
)
from custom_components.tapo_event_bridge.models import (
    DiscoveredEntity,
    EvidenceLevel,
)


def test_capabilities_are_inferred_from_registry_text() -> None:
    entities = [
        DiscoveredEntity(
            entity_id="binary_sensor.garden_motion",
            platform="tapo_control",
            device_id="device",
        ),
        DiscoveredEntity(
            entity_id="light.garden_floodlight",
            platform="tapo_control",
            device_id="device",
        ),
        DiscoveredEntity(
            entity_id="sensor.garden_battery",
            platform="tapo_control",
            device_id="device",
        ),
    ]

    capabilities = infer_capabilities(entities)

    assert capabilities["motion_detection"].value is True
    assert capabilities["spotlight"].value is True
    assert capabilities["battery"].value is True


def test_missing_capability_stays_unknown() -> None:
    fact = capability_fact({}, "rtsp")

    assert fact.value is None
    assert fact.evidence is EvidenceLevel.UNKNOWN
