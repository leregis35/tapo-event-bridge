"""Diagnostic sensors for Tapo Event Bridge."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory, UnitOfTime

from .entity import TapoEventBridgeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import TapoEventBridgeConfigEntry
    from .runtime import TapoEventBridgeRuntime


ValueFunction = Callable[["TapoEventBridgeRuntime"], Any]


class BridgeSensor(TapoEventBridgeEntity, SensorEntity):
    """A push-updated diagnostic sensor backed by runtime state."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        runtime: TapoEventBridgeRuntime,
        entry_id: str,
        key: str,
        value_fn: ValueFunction,
        *,
        native_unit: str | None = None,
    ) -> None:
        """Initialize the diagnostic sensor."""
        super().__init__(runtime, entry_id, key)
        self._attr_translation_key = key
        self._value_fn = value_fn
        self._attr_native_unit_of_measurement = native_unit

    @property
    def native_value(self) -> Any:
        """Return the latest runtime-derived value."""
        return self._value_fn(self._runtime)


class LastEventSensor(BridgeSensor):
    """Expose the latest normalized event with useful attributes."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return privacy-conscious details for the latest event."""
        event = self._runtime.latest_event
        return {} if event is None else event.as_dict()


def _latest_event_type(runtime: TapoEventBridgeRuntime) -> str:
    event = runtime.latest_event
    return "none" if event is None else event.event_type.value


def _latest_event_source(runtime: TapoEventBridgeRuntime) -> str:
    event = runtime.latest_event
    return "none" if event is None else event.source.value


def _latest_event_latency(runtime: TapoEventBridgeRuntime) -> float | None:
    event = runtime.latest_event
    return None if event is None else round(event.latency_ms, 3)


def _active_transports(runtime: TapoEventBridgeRuntime) -> str:
    return ", ".join(runtime.transports) if runtime.transports else "none"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bridge diagnostic sensors."""
    runtime = entry.runtime_data
    entry_id = entry.entry_id
    async_add_entities(
        (
            BridgeSensor(runtime, entry_id, "status", lambda value: value.status),
            BridgeSensor(
                runtime,
                entry_id,
                "camera_count",
                lambda value: len(value.cameras),
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "recorded_event_count",
                lambda value: value.recorded_event_count,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "active_transports",
                _active_transports,
            ),
            LastEventSensor(
                runtime,
                entry_id,
                "last_event",
                _latest_event_type,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "last_event_source",
                _latest_event_source,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "last_event_latency",
                _latest_event_latency,
                native_unit=UnitOfTime.MILLISECONDS,
            ),
        )
    )
