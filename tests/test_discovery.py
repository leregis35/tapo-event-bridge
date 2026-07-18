"""Tests for low-cost registry discovery."""

from custom_components.tapo_event_bridge.discovery import (
    build_camera_diagnostics,
    privacy_safe_identifier,
)
from custom_components.tapo_event_bridge.models import (
    DiscoveredDevice,
    DiscoveredEntity,
    EvidenceLevel,
)


def test_privacy_identifier_is_stable_and_redacted() -> None:
    first = privacy_safe_identifier("raw-ha-device-id")
    second = privacy_safe_identifier("raw-ha-device-id")

    assert first == second
    assert first.startswith("camera-")
    assert "raw-ha-device-id" not in first


def test_discovers_tapo_camera_from_manufacturer() -> None:
    devices = [
        DiscoveredDevice(
            device_id="garage-device",
            name="Garage",
            manufacturer="TP-Link",
            model="C520WS",
            sw_version="1.2.3",
        )
    ]
    entities = [
        DiscoveredEntity(
            entity_id="camera.garage_hd_stream",
            platform="tapo_control",
            device_id="garage-device",
        ),
        DiscoveredEntity(
            entity_id="binary_sensor.garage_person_detection",
            platform="tapo_control",
            device_id="garage-device",
        ),
    ]

    cameras = build_camera_diagnostics(devices, entities)

    assert len(cameras) == 1
    camera = cameras[0]
    assert camera.name == "Garage"
    assert camera.model.value == "C520WS"
    assert camera.capabilities["person_detection"].value is True
    assert camera.capabilities["person_detection"].evidence is EvidenceLevel.OBSERVED
    assert camera.entity_count == 2


def test_discovers_tapo_camera_from_platform() -> None:
    devices = [DiscoveredDevice(device_id="camera-device", name="Entrée")]
    entities = [
        DiscoveredEntity(
            entity_id="camera.entree",
            platform="tapo",
            device_id="camera-device",
        )
    ]

    cameras = build_camera_diagnostics(devices, entities)

    assert len(cameras) == 1
    assert cameras[0].source_platforms == ("tapo",)


def test_ignores_unrelated_device() -> None:
    devices = [
        DiscoveredDevice(
            device_id="unrelated",
            name="Thermostat",
            manufacturer="Other",
        )
    ]
    entities = [
        DiscoveredEntity(
            entity_id="sensor.thermostat_temperature",
            platform="other",
            device_id="unrelated",
        )
    ]

    assert build_camera_diagnostics(devices, entities) == ()


def test_disabled_entities_do_not_create_capabilities() -> None:
    devices = [
        DiscoveredDevice(
            device_id="camera-device",
            manufacturer="Tapo",
        )
    ]
    entities = [
        DiscoveredEntity(
            entity_id="camera.camera_device",
            platform="tapo_control",
            device_id="camera-device",
        ),
        DiscoveredEntity(
            entity_id="binary_sensor.camera_device_vehicle_detection",
            platform="tapo_control",
            device_id="camera-device",
            disabled=True,
        ),
    ]

    camera = build_camera_diagnostics(devices, entities)[0]

    assert "vehicle_detection" not in camera.capabilities
