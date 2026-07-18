"""Binary diagnostic sensors for Tapo Event Bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import EntityCategory

from .entity import TapoEventBridgeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import TapoEventBridgeConfigEntry
    from .runtime import TapoEventBridgeRuntime


class BridgeHealthBinarySensor(TapoEventBridgeEntity, BinarySensorEntity):
    """Report whether the local bridge runtime is healthy."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "healthy"

    @property
    def is_on(self) -> bool:
        """Return true unless the runtime entered an error state."""
        return self._runtime.status != "error"


class CamerasDiscoveredBinarySensor(TapoEventBridgeEntity, BinarySensorEntity):
    """Report whether at least one Tapo camera was discovered."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "cameras_discovered"

    @property
    def is_on(self) -> bool:
        """Return true when discovery found at least one camera."""
        return bool(self._runtime.cameras)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge binary sensors."""
    runtime: TapoEventBridgeRuntime = entry.runtime_data
    entry_id = entry.entry_id
    async_add_entities(
        (
            BridgeHealthBinarySensor(runtime, entry_id, "healthy"),
            CamerasDiscoveredBinarySensor(
                runtime,
                entry_id,
                "cameras_discovered",
            ),
        )
    )
