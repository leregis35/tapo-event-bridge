"""Runtime state for Tapo Event Bridge."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import monotonic

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
    last_discovery_at: datetime | None = None
    last_discovery_duration_ms: float | None = None
    last_discovery_error: str | None = None
    _listeners: dict[int, RuntimeListener] = field(default_factory=dict, repr=False)
    _cleanup_callbacks: list[Callable[[], None]] = field(
        default_factory=list,
        repr=False,
    )
    _next_listener_id: int = field(default=1, repr=False)
    _discovery_started_at: float | None = field(default=None, repr=False)

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

    @property
    def entity_count(self) -> int:
        """Return the total number of camera entities observed."""
        return sum(camera.entity_count for camera in self.cameras.values())

    @property
    def capability_count(self) -> int:
        """Return the total number of observed camera capabilities."""
        return sum(len(camera.capabilities) for camera in self.cameras.values())

    @property
    def capability_explorer_state(self) -> str:
        """Return the high-level state of the Capability Explorer."""
        if self.last_discovery_error:
            return "error"
        if self.status == "discovering":
            return "scanning"
        if not self.cameras:
            return "no_cameras"
        return "ready"

    @property
    def average_camera_health(self) -> int | None:
        """Return the average registry-evidence completeness score."""
        cameras = tuple(self.cameras.values())
        if not cameras:
            return None
        return round(sum(camera.health_score for camera in cameras) / len(cameras))


    @property
    def fleet_insights(self) -> dict[str, object]:
        """Return privacy-safe fleet analytics from registry-only evidence."""
        cameras = tuple(self.cameras.values())
        model_distribution: dict[str, int] = {}
        power_distribution: dict[str, int] = {}
        platform_distribution: dict[str, int] = {}
        domain_distribution: dict[str, int] = {}
        capability_coverage: dict[str, int] = {}
        attention: list[dict[str, object]] = []

        for camera in cameras:
            model = str(camera.model.value or "unknown")
            model_distribution[model] = model_distribution.get(model, 0) + 1

            power = camera.power_source
            power_distribution[power] = power_distribution.get(power, 0) + 1

            for platform in camera.source_platforms:
                platform_distribution[platform] = (
                    platform_distribution.get(platform, 0) + 1
                )
            for domain, count in camera.entity_domains.items():
                domain_distribution[domain] = domain_distribution.get(domain, 0) + count
            for capability in camera.capabilities:
                capability_coverage[capability] = (
                    capability_coverage.get(capability, 0) + 1
                )

            reasons: list[str] = []
            if not camera.model.value:
                reasons.append("model_unknown")
            if camera.entity_count == 0:
                reasons.append("no_entities")
            if not camera.capabilities:
                reasons.append("no_observed_capabilities")
            if camera.health_score < 80:
                reasons.append("low_evidence_completeness")
            if reasons:
                attention.append(
                    {
                        "identifier": camera.identifier,
                        "name": camera.name,
                        "health_score": camera.health_score,
                        "reasons": reasons,
                    }
                )

        average = self.average_camera_health
        if self.last_discovery_error:
            grade = "error"
        elif not cameras:
            grade = "empty"
        elif average is not None and average >= 90 and not attention:
            grade = "excellent"
        elif average is not None and average >= 75:
            grade = "good"
        else:
            grade = "attention"

        camera_count = len(cameras)
        coverage_percent = {
            capability: round(count * 100 / camera_count)
            for capability, count in sorted(capability_coverage.items())
        } if camera_count else {}

        return {
            "grade": grade,
            "camera_count": camera_count,
            "average_camera_health": average,
            "cameras_needing_attention": sorted(
                attention, key=lambda item: str(item["identifier"])
            ),
            "model_distribution": dict(sorted(model_distribution.items())),
            "power_distribution": dict(sorted(power_distribution.items())),
            "platform_distribution": dict(sorted(platform_distribution.items())),
            "entity_domain_distribution": dict(sorted(domain_distribution.items())),
            "capability_coverage_percent": coverage_percent,
            "observed_capability_count": self.capability_count,
            "entity_count": self.entity_count,
            "last_scan": (
                None
                if self.last_discovery_at is None
                else self.last_discovery_at.isoformat()
            ),
            "scan_duration_ms": self.last_discovery_duration_ms,
            "last_error": self.last_discovery_error,
            "data_policy": (
                "Registry-only analytics: no network polling and no camera wake-up."
            ),
        }

    @property
    def event_activity(self) -> dict[str, object]:
        """Return bounded, in-memory activity analytics for normalized events."""
        events = self.event_engine.recorder.snapshot()
        by_type: dict[str, int] = {}
        by_source: dict[str, int] = {}
        by_camera: dict[str, int] = {}
        active: dict[str, list[str]] = {}

        for event in events:
            event_type = event.event_type.value
            source = event.source.value
            by_type[event_type] = by_type.get(event_type, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
            by_camera[event.camera_id] = by_camera.get(event.camera_id, 0) + 1

            active_types = active.setdefault(event.camera_id, [])
            if event.state.value == "started" and event_type not in active_types:
                active_types.append(event_type)
            elif event.state.value == "ended" and event_type in active_types:
                active_types.remove(event_type)

        active = {
            camera_id: sorted(types)
            for camera_id, types in sorted(active.items())
            if types
        }
        recent = [event.as_dict() for event in events[-20:]]
        return {
            "total": len(events),
            "by_type": dict(sorted(by_type.items())),
            "by_source": dict(sorted(by_source.items())),
            "by_camera": dict(sorted(by_camera.items())),
            "active_events": active,
            "recent_events": recent,
            "buffer_limit": self.event_engine.recorder.max_events,
            "data_policy": "Bounded memory only; no database writes or polling.",
        }

    @property
    def dashboard_snapshot(self) -> dict[str, object]:
        """Return a stable, compact schema for Lovelace dashboards."""
        insights = self.fleet_insights
        activity = self.event_activity
        latest = self.latest_event
        cameras = [
            {
                "identifier": camera.identifier,
                "name": camera.name,
                "model": camera.model.value,
                "power_source": camera.power_source,
                "health_score": camera.health_score,
                "entity_count": camera.entity_count,
                "capabilities": sorted(camera.capabilities),
                "active_events": activity["active_events"].get(
                    camera.identifier, []
                ),
                "event_count": activity["by_camera"].get(camera.identifier, 0),
            }
            for _, camera in sorted(self.cameras.items())
        ]
        return {
            "schema_version": 1,
            "status": self.status,
            "health_score": self.health_score,
            "fleet_grade": insights["grade"],
            "camera_count": len(cameras),
            "entity_count": self.entity_count,
            "capability_count": self.capability_count,
            "recorded_event_count": self.recorded_event_count,
            "active_event_count": sum(
                len(types) for types in activity["active_events"].values()
            ),
            "last_event": None if latest is None else latest.as_dict(),
            "event_types": activity["by_type"],
            "power_distribution": insights["power_distribution"],
            "capability_coverage_percent": insights[
                "capability_coverage_percent"
            ],
            "cameras_needing_attention": insights[
                "cameras_needing_attention"
            ],
            "last_scan": insights["last_scan"],
            "scan_duration_ms": insights["scan_duration_ms"],
            "cameras": cameras,
            "data_policy": (
                "Registry and Home Assistant state events only; no direct polling."
            ),
        }

    @property
    def health_score(self) -> int:
        """Return a conservative runtime health score from observable state."""
        if self.last_discovery_error:
            return 25
        if self.status == "discovering":
            return 75
        if self.status == "starting":
            return 50
        if not self.cameras:
            return 60
        return 100

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

    def begin_discovery(self) -> None:
        """Mark a registry-only discovery pass as running."""
        self.status = "discovering"
        self.last_discovery_error = None
        self._discovery_started_at = monotonic()
        self._notify_listeners()

    def complete_discovery(
        self,
        cameras: tuple[CameraDiagnostic, ...],
    ) -> None:
        """Store discovery results and timing metadata."""
        self.registry.replace(cameras)
        self.status = "discovery_ready"
        self.last_discovery_at = datetime.now(UTC)
        if self._discovery_started_at is not None:
            self.last_discovery_duration_ms = round(
                (monotonic() - self._discovery_started_at) * 1000,
                3,
            )
        self._discovery_started_at = None
        self._notify_listeners()

    def fail_discovery(self, error: Exception) -> None:
        """Record a discovery failure without retaining a traceback."""
        self.status = "discovery_error"
        self.last_discovery_error = type(error).__name__
        if self._discovery_started_at is not None:
            self.last_discovery_duration_ms = round(
                (monotonic() - self._discovery_started_at) * 1000,
                3,
            )
        self._discovery_started_at = None
        self._notify_listeners()

    def replace_cameras(self, cameras: tuple[CameraDiagnostic, ...]) -> None:
        """Replace discovery results for backwards-compatible callers."""
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
