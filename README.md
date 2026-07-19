# Tapo Event Bridge

Home Assistant companion integration for normalized Tapo camera events,
registry-based discovery, fleet diagnostics and dashboard-ready analytics.

## Version 1.0

Tapo Event Bridge 1.0 establishes the first stable project contract:

- discovers TP-Link/Tapo cameras from Home Assistant registries;
- normalizes existing Home Assistant camera and detection state changes;
- publishes `tapo_event_bridge_event` on the Home Assistant event bus;
- retains a bounded in-memory event buffer with duplicate suppression;
- exposes camera inventory, capability, fleet and dashboard diagnostics;
- provides runtime telemetry and diagnostic actions;
- performs no direct camera polling and does not intentionally wake battery
  cameras.

## Native Home Assistant entities

The integration provides sensors for runtime status, camera inventory,
capabilities, fleet intelligence, event activity, dashboard data and runtime
metrics. It also provides diagnostic binary sensors and buttons for rediscovery,
replay and clearing the in-memory event buffer.

## Resource and privacy policy

Entities are push-updated from runtime listeners. Registry discovery runs at
startup or on demand. Event processing is in memory, bounded and local. The
integration does not make direct camera requests, write its own database or
store raw camera payloads in diagnostics.

## Home Assistant event

Normalized events are emitted as:

```text
tapo_event_bridge_event
```

The payload contains normalized type, source, state, timestamps, confidence,
latency and privacy-conscious metadata.

## Development checks

```bash
uv sync --dev
uv run ruff check .
uv run pytest
```

## Test camera lab

C211, C220, C425, C520WS ×2 and C660.
