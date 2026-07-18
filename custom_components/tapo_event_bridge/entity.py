"""Shared Home Assistant entity support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, NAME, VERSION

if TYPE_CHECKING:
    from collections.abc import Callable

    from .runtime import TapoEventBridgeRuntime


class TapoEventBridgeEntity(Entity):
    """Base class for push-updated bridge entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        runtime: TapoEventBridgeRuntime,
        entry_id: str,
        key: str,
    ) -> None:
        """Initialize a bridge entity."""
        self._runtime = runtime
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=NAME,
            manufacturer="Tapo Event Bridge",
            model="Camera event bridge",
            sw_version=VERSION,
        )
        self._remove_runtime_listener: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime push updates."""
        self._remove_runtime_listener = self._runtime.subscribe(
            self._handle_runtime_update
        )

    async def async_will_remove_from_hass(self) -> None:
        """Release the runtime subscription."""
        if self._remove_runtime_listener is not None:
            self._remove_runtime_listener()
            self._remove_runtime_listener = None

    def _handle_runtime_update(self) -> None:
        """Write fresh state after a runtime change."""
        self.async_write_ha_state()
