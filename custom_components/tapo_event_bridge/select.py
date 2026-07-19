"""Event-journal filters for Tapo Event Bridge."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory

from .entity import TapoEventBridgeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import TapoEventBridgeConfigEntry
    from .runtime import TapoEventBridgeRuntime


class JournalCameraFilterSelect(TapoEventBridgeEntity, SelectEntity):
    """Select the camera shown in the event journal."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "journal_camera_filter"

    @property
    def options(self) -> list[str]:
        """Return available camera filters."""
        return list(self._runtime.journal_camera_options)

    @property
    def current_option(self) -> str:
        """Return the selected camera filter."""
        return self._runtime.journal_camera_filter

    async def async_select_option(self, option: str) -> None:
        """Apply a camera filter without camera I/O."""
        self._runtime.set_journal_camera_filter(option)


class JournalEventTypeFilterSelect(TapoEventBridgeEntity, SelectEntity):
    """Select the event type shown in the event journal."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "journal_event_type_filter"

    @property
    def options(self) -> list[str]:
        """Return available event-type filters."""
        return list(self._runtime.journal_event_type_options)

    @property
    def current_option(self) -> str:
        """Return the selected event-type filter."""
        return self._runtime.journal_event_type_filter

    async def async_select_option(self, option: str) -> None:
        """Apply an event-type filter without camera I/O."""
        self._runtime.set_journal_event_type_filter(option)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up event-journal filter selects."""
    runtime: TapoEventBridgeRuntime = entry.runtime_data
    entry_id = entry.entry_id
    async_add_entities(
        (
            JournalCameraFilterSelect(
                runtime,
                entry_id,
                "journal_camera_filter",
            ),
            JournalEventTypeFilterSelect(
                runtime,
                entry_id,
                "journal_event_type_filter",
            ),
        )
    )
