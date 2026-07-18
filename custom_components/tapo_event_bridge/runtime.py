"""Runtime state for Tapo Event Bridge."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .event_engine import EventEngine
from .events import CameraEvent, EventSource
from .models import CameraDiagnostic
from .registry import CameraRegistry

type RuntimeListener = Callable[[], None]


@dataclass(slots=True)
class TapoEventBridgeRuntime:
    """Runtime data attached to the Home Assistant config entry."""

    status: str = "starting"
    registry: CameraRegistry = field(default_factory=CameraRegistry)
    event_engine: EventEngine = field(default_factory=EventEngine)
    transports: list[str] = field(default_factory=list)
    _listeners: dict[int, RuntimeListener] = field(default_factory=dict, repr=False)
    _cleanup_callbacks: list[Callable[[], None]] = field(
        default_factory=list,
        repr=False,
    )
    _next_listener_id: int = field(default=1, repr=False)

    @property
    def cameras(self) -> dict[str, CameraDiagnostic]:
        """Return a camera mapping for diagnostics and platforms."""
        return self.registry.as_dict()

    @property
    def latest_event(self) -> CameraEvent | None:
        """Return the newest recorded event, if available."""
        events = self.event_engine.recorder.snapshot(limit=1)
        return events[-1] if events else None

    @property
    def recorded_event_count(self) -> int:
        """Return the number of events currently retained in memory."""
        return len(self.event_engine.recorder)

    def subscribe(self, listener: RuntimeListener) -> Callable[[], None]:
        """Subscribe to runtime changes and return an idempotent unsubscribe."""
        listener_id = self._next_listener_id
        self._next_listener_id += 1
        self._listeners[listener_id] = listener

        def unsubscribe() -> None:
            self._listeners.pop(listener_id, None)

        return unsubscribe

    def add_cleanup_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to run when the runtime is closed."""
        self._cleanup_callbacks.append(callback)

    def replace_cameras(self, cameras: tuple[CameraDiagnostic, ...]) -> None:
        """Replace discovery results and update runtime status."""
        self.registry.replace(cameras)
        self.status = "discovery_ready"
        self._notify_listeners()

    async def publish_event(self, event: CameraEvent) -> None:
        """Publish one normalized event through the runtime engine."""
        await self.event_engine.publish(event)
        self.status = "event_ready"
        self._notify_listeners()

    async def replay_last_event(self) -> CameraEvent | None:
        """Replay the newest non-replay event once."""
        events = self.event_engine.recorder.snapshot()
        original = next(
            (
                event
                for event in reversed(events)
                if event.source is not EventSource.REPLAY
            ),
            None,
        )
        if original is None:
            return None
        replayed = original.as_replay()
        await self.publish_event(replayed)
        return replayed

    def close(self) -> None:
        """Release subscriptions and runtime callbacks."""
        for callback in tuple(self._cleanup_callbacks):
            callback()
        self._cleanup_callbacks.clear()
        self._listeners.clear()

    def _notify_listeners(self) -> None:
        """Notify a stable snapshot of runtime listeners."""
        for listener in tuple(self._listeners.values()):
            listener()
