"""Configuration switches for Tapo Event Bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory

from .entity import TapoEventBridgeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import TapoEventBridgeConfigEntry
    from .runtime import TapoEventBridgeRuntime


class PersonLightingSwitch(TapoEventBridgeEntity, SwitchEntity):
    """Enable person-detection lighting using camera-local light entities."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "person_lighting"

    @property
    def is_on(self) -> bool:
        """Return whether person lighting is enabled."""
        return self._runtime.person_lighting_enabled

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable person lighting."""
        self._runtime.set_person_lighting_enabled(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable person lighting."""
        self._runtime.set_person_lighting_enabled(False)


class StateProbeSwitch(TapoEventBridgeEntity, SwitchEntity):
    """Arm the opt-in Home Assistant state-change diagnostic probe."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "state_probe"

    @property
    def is_on(self) -> bool:
        """Return whether the state probe is armed."""
        return self._runtime.state_probe_enabled

    async def async_turn_on(self, **kwargs: object) -> None:
        """Arm the state probe."""
        self._runtime.set_state_probe_enabled(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disarm the state probe."""
        self._runtime.set_state_probe_enabled(False)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge configuration switches."""
    runtime: TapoEventBridgeRuntime = entry.runtime_data
    async_add_entities(
        (
            PersonLightingSwitch(runtime, entry.entry_id, "person_lighting"),
            StateProbeSwitch(runtime, entry.entry_id, "state_probe"),
        )
    )
