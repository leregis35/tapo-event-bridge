"""Action buttons for Tapo Event Bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory

from .discovery import async_discover_cameras
from .entity import TapoEventBridgeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import TapoEventBridgeConfigEntry
    from .runtime import TapoEventBridgeRuntime


class RediscoverCamerasButton(TapoEventBridgeEntity, ButtonEntity):
    """Refresh the registry-only camera inventory on demand."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "rediscover_cameras"

    async def async_press(self) -> None:
        """Read Home Assistant registries once without camera polling."""
        self._runtime.begin_discovery()
        try:
            cameras = await async_discover_cameras(self.hass)
        except Exception as error:
            self._runtime.fail_discovery(error)
            raise
        self._runtime.complete_discovery(cameras)


class ReplayLastEventButton(TapoEventBridgeEntity, ButtonEntity):
    """Replay the newest original event through the normalized pipeline."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "replay_last_event"

    @property
    def available(self) -> bool:
        """Return true when at least one original event can be replayed."""
        return self._runtime.recorded_event_count > 0

    async def async_press(self) -> None:
        """Replay the newest non-replay event."""
        await self._runtime.replay_last_event()


class ClearEventHistoryButton(TapoEventBridgeEntity, ButtonEntity):
    """Clear the bounded in-memory event history."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "clear_event_history"

    @property
    def available(self) -> bool:
        """Return true when the event buffer contains data."""
        return self._runtime.recorded_event_count > 0

    async def async_press(self) -> None:
        """Clear retained events without touching Home Assistant history."""
        self._runtime.clear_events()


class ClearStateProbeButton(TapoEventBridgeEntity, ButtonEntity):
    """Clear the bounded in-memory diagnostic state probe."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "clear_state_probe"

    @property
    def available(self) -> bool:
        """Return true when the probe contains captured changes."""
        return bool(self._runtime.state_probe_entries)

    async def async_press(self) -> None:
        """Clear captured state changes."""
        self._runtime.clear_state_probe()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge action buttons."""
    runtime: TapoEventBridgeRuntime = entry.runtime_data
    entry_id = entry.entry_id
    async_add_entities(
        (
            RediscoverCamerasButton(
                runtime,
                entry_id,
                "rediscover_cameras",
            ),
            ReplayLastEventButton(
                runtime,
                entry_id,
                "replay_last_event",
            ),
            ClearEventHistoryButton(
                runtime,
                entry_id,
                "clear_event_history",
            ),
            ClearStateProbeButton(
                runtime,
                entry_id,
                "clear_state_probe",
            ),
        )
    )
