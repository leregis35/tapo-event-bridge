"""Tapo Event Bridge integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import EVENT_CAMERA, PLATFORMS
from .discovery import async_discover_cameras
from .ha_event_bridge import async_subscribe_home_assistant_events
from .runtime import TapoEventBridgeRuntime

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    type TapoEventBridgeConfigEntry = ConfigEntry[TapoEventBridgeRuntime]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
) -> bool:
    """Set up Tapo Event Bridge from a config entry."""
    runtime = TapoEventBridgeRuntime()
    entry.runtime_data = runtime

    def forward_event(event: object) -> None:
        """Expose normalized events on the Home Assistant event bus."""
        from .events import CameraEvent

        if isinstance(event, CameraEvent):
            hass.bus.async_fire(EVENT_CAMERA, event.as_dict())

    runtime.add_cleanup_callback(runtime.event_engine.subscribe(forward_event))
    runtime.begin_discovery()
    try:
        cameras = await async_discover_cameras(hass)
    except Exception as error:
        runtime.fail_discovery(error)
        raise
    runtime.complete_discovery(cameras)
    runtime.add_cleanup_callback(
        await async_subscribe_home_assistant_events(hass, runtime)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: TapoEventBridgeConfigEntry,
) -> bool:
    """Unload a Tapo Event Bridge config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        entry.runtime_data.close()
    return unloaded
