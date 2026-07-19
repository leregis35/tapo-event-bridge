"""Diagnostic sensors for Tapo Event Bridge."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory, UnitOfTime

from .attributes import build_capability_explorer_attributes
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


class CameraInventorySensor(BridgeSensor):
    """Expose compact, live inventory details for discovered cameras."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return one compact summary per discovered camera."""
        return {
            "cameras": [
                camera.summary()
                for _, camera in sorted(self._runtime.cameras.items())
            ]
        }


class EventActivitySensor(BridgeSensor):
    """Expose normalized activity captured from existing HA entities."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return bounded event statistics and recent normalized events."""
        return self._runtime.event_activity


class FleetInsightsSensor(BridgeSensor):
    """Expose fleet-wide analytics without querying any camera."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return deterministic analytics computed from registry evidence."""
        return self._runtime.fleet_insights


class DashboardSnapshotSensor(BridgeSensor):
    """Expose a stable payload designed for Lovelace presentation."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the dashboard schema without triggering camera I/O."""
        return self._runtime.dashboard_snapshot


class RuntimeMetricsSensor(BridgeSensor):
    """Expose lightweight runtime telemetry for production diagnostics."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return stable, in-memory runtime metrics."""
        return self._runtime.runtime_metrics


class CapabilityExplorerSensor(BridgeSensor):
    """Expose a detailed, evidence-labelled profile for every camera."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return a compact profile safe for Home Assistant Recorder."""
        return build_capability_explorer_attributes(self._runtime)



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


def _last_discovery(runtime: TapoEventBridgeRuntime) -> str | None:
    value = runtime.last_discovery_at
    return None if value is None else value.isoformat()


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
            CameraInventorySensor(
                runtime,
                entry_id,
                "camera_count",
                lambda value: len(value.cameras),
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "entity_count",
                lambda value: value.entity_count,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "capability_count",
                lambda value: value.capability_count,
            ),

            FleetInsightsSensor(
                runtime,
                entry_id,
                "fleet_insights",
                lambda value: str(value.fleet_insights["grade"]),
            ),
            CapabilityExplorerSensor(
                runtime,
                entry_id,
                "capability_explorer",
                lambda value: value.capability_explorer_state,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "health_score",
                lambda value: value.health_score,
                native_unit="%",
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "last_discovery",
                _last_discovery,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "discovery_duration",
                lambda value: value.last_discovery_duration_ms,
                native_unit=UnitOfTime.MILLISECONDS,
            ),
            BridgeSensor(
                runtime,
                entry_id,
                "recorded_event_count",
                lambda value: value.recorded_event_count,
            ),
            EventActivitySensor(
                runtime,
                entry_id,
                "event_activity",
                lambda value: value.recorded_event_count,
            ),
            DashboardSnapshotSensor(
                runtime,
                entry_id,
                "dashboard_snapshot",
                lambda value: str(value.dashboard_snapshot["fleet_grade"]),
            ),
            RuntimeMetricsSensor(
                runtime,
                entry_id,
                "runtime_metrics",
                lambda value: value.uptime_seconds,
                native_unit=UnitOfTime.SECONDS,
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
