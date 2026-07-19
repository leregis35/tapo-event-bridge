"""Configuration numbers for Tapo Event Bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTime

from .entity import TapoEventBridgeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import TapoEventBridgeConfigEntry
    from .runtime import TapoEventBridgeRuntime


class PersonLightingDurationNumber(TapoEventBridgeEntity, NumberEntity):
    """Configure how long lights remain on after a person event."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "person_lighting_duration"
    _attr_native_min_value = 10
    _attr_native_max_value = 900
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.BOX

    @property
    def native_value(self) -> float:
        """Return the configured duration."""
        return float(self._runtime.person_lighting_duration_seconds)

    async def async_set_native_value(self, value: float) -> None:
        """Apply the configured duration."""
        self._runtime.set_person_lighting_duration(int(value))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge configuration numbers."""
    runtime: TapoEventBridgeRuntime = entry.runtime_data
    async_add_entities(
        (
            PersonLightingDurationNumber(
                runtime,
                entry.entry_id,
                "person_lighting_duration",
            ),
        )
    )
