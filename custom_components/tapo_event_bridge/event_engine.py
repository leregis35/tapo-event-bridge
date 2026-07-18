"""Low-overhead event recording, dispatch, and replay."""

from __future__ import annotations

import inspect
from collections import deque
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field

from .events import CameraEvent, EventType

type EventCallback = Callable[[CameraEvent], Awaitable[None] | None]


@dataclass(slots=True)
class EventRecorder:
    """Bounded in-memory recorder; it performs no disk or network I/O."""

    max_events: int = 200
    _events: deque[CameraEvent] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_events < 1:
            raise ValueError("max_events must be at least 1")
        self._events = deque(maxlen=self.max_events)

    def record(self, event: CameraEvent) -> None:
        """Store one event, evicting the oldest when the buffer is full."""
        self._events.append(event)

    def snapshot(
        self,
        *,
        camera_id: str | None = None,
        event_type: EventType | None = None,
        limit: int | None = None,
    ) -> tuple[CameraEvent, ...]:
        """Return matching events from oldest to newest."""
        events: Iterable[CameraEvent] = self._events
        if camera_id is not None:
            events = (event for event in events if event.camera_id == camera_id)
        if event_type is not None:
            events = (event for event in events if event.event_type is event_type)
        result = tuple(events)
        if limit is None:
            return result
        if limit < 0:
            raise ValueError("limit must not be negative")
        if limit == 0:
            return ()
        return result[-limit:]

    def clear(self) -> None:
        """Discard all recorded events."""
        self._events.clear()

    def __len__(self) -> int:
        return len(self._events)


@dataclass(slots=True)
class EventEngine:
    """Normalize event flow without polling cameras or using background tasks."""

    recorder: EventRecorder = field(default_factory=EventRecorder)
    developer_mode: bool = False
    _subscribers: dict[int, EventCallback] = field(default_factory=dict, repr=False)
    _next_subscription_id: int = field(default=1, repr=False)

    def subscribe(self, callback: EventCallback) -> Callable[[], None]:
        """Register a callback and return an idempotent unsubscribe function."""
        subscription_id = self._next_subscription_id
        self._next_subscription_id += 1
        self._subscribers[subscription_id] = callback

        def unsubscribe() -> None:
            self._subscribers.pop(subscription_id, None)

        return unsubscribe

    async def publish(self, event: CameraEvent) -> None:
        """Record and dispatch an event to a stable subscriber snapshot."""
        self.recorder.record(event)
        for callback in tuple(self._subscribers.values()):
            result = callback(event)
            if inspect.isawaitable(result):
                await result

    async def replay(
        self,
        *,
        camera_id: str | None = None,
        event_type: EventType | None = None,
        limit: int | None = None,
    ) -> tuple[CameraEvent, ...]:
        """Replay matching recorded events once, preserving original history."""
        originals = self.recorder.snapshot(
            camera_id=camera_id,
            event_type=event_type,
            limit=limit,
        )
        replayed = tuple(event.as_replay() for event in originals)
        for event in replayed:
            await self.publish(event)
        return replayed

    def diagnostic_snapshot(self) -> dict[str, object]:
        """Return an anonymized event-engine status snapshot."""
        latest = self.recorder.snapshot(limit=20 if self.developer_mode else 5)
        return {
            "developer_mode": self.developer_mode,
            "recorded_event_count": len(self.recorder),
            "subscriber_count": len(self._subscribers),
            "recent_events": [event.as_dict() for event in latest],
        }
