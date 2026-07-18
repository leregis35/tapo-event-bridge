# Changelog

## 0.4.0 - Sprint 5 Home Assistant entities

- Forward the config entry to native sensor, binary sensor, and button platforms.
- Add push-updated runtime status, discovery, event, source, and latency sensors.
- Add bridge-health and cameras-discovered binary sensors.
- Add on-demand registry rediscovery and safe last-event replay buttons.
- Publish normalized camera events to the Home Assistant event bus.
- Add runtime listeners and deterministic cleanup during config-entry unload.
- Include event-engine state in privacy-safe diagnostics.

## 0.3.0 - Sprint 4 event engine

- Add normalized camera event types, states, sources, timestamps, and latency.
- Add a bounded, in-memory recorder with filtering and zero disk I/O.
- Add synchronous and asynchronous event subscribers.
- Add safe event replay with fresh identifiers and stripped raw payloads.
- Add developer-mode diagnostics without background tasks or polling.
- Integrate the event engine into runtime state.
- Expand unit coverage for validation, recording, dispatch, replay, and runtime.

## 0.2.0 - Sprint 3 discovery engine

- Discover Tapo cameras from Home Assistant device and entity registries.
- Add a privacy-safe camera registry.
- Infer capabilities conservatively from exposed entities.
- Add anonymized JSON-serializable discovery exports.
- Avoid all direct camera polling and battery-camera wakeups.
- Expand unit coverage for discovery, capabilities, registry, and exports.

## 0.1.0

- Initial Home Assistant config flow.
- Runtime and diagnostic data models.
- Privacy-safe integration diagnostics.
