# Tapo Event Bridge

Experimental Home Assistant custom integration focused on reliable, normalized
Tapo camera events.

> Current status: Sprint 5 Home Assistant entities. The bridge now exposes its
> discovery and event-engine state as native push-updated entities, while real
> camera event transports remain the next milestone.

## What 0.4.0 does

- Discovers Tapo/TP-Link cameras from Home Assistant registries without polling.
- Provides native diagnostic sensors for status, camera count, retained events,
  active transports, latest event, source, and latency.
- Provides binary sensors for bridge health and camera discovery.
- Provides buttons for registry-only rediscovery and safe replay of the latest
  original event.
- Fires normalized events on the Home Assistant event bus as
  `tapo_event_bridge_event`.
- Records events in a bounded in-memory buffer with no disk writes.
- Exports privacy-conscious config-entry diagnostics.
- Performs no direct camera request and no battery-camera wakeup.

## Resource policy

Entities are push-updated from runtime listeners. There is no entity polling,
background task, disk write, or automatic camera-network request. Rediscovery
reads Home Assistant registries only and runs at startup or when requested.

## Home Assistant event

Normalized events are emitted on the Home Assistant event bus:

```text
tapo_event_bridge_event
```

The payload contains normalized type, source, state, timestamps, confidence,
latency, and privacy-conscious metadata.

## Development checks

```bash
uv sync --dev
uv run ruff check .
uv run pytest
```

## Test camera lab

C211, C220, C425, C520WS ×2, and C660.
