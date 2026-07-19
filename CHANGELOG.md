# Changelog

## 1.1.0 - Native Event Journal

- Added a compact, Recorder-safe event journal sensor.
- Added camera and event-type journal filters as native Home Assistant selects.
- Added newest-first, bounded journal entries with latency and confidence.
- Kept all journal data in memory with no direct camera polling.
- Added tests for filtering, validation, ordering, and the 16 KiB Recorder limit.

## 1.0.1 - Recorder-safe Capability Explorer

- Reduced Capability Explorer state attributes below Home Assistant Recorder limits.
- Kept detailed evidence in downloadable Home Assistant diagnostics.
- Added deterministic camera and capability bounds for future large fleets.
- Added regression tests for attribute payload size and diagnostic completeness.


## 1.0.0 - Production Foundation

- Added duplicate-event suppression for noisy Home Assistant state sources.
- Added runtime uptime, buffer, listener, transport, and suppression telemetry.
- Added a diagnostic action to clear the bounded in-memory event history.
- Stabilized the dashboard schema introduced in 0.9.0.
- Preserved the battery-safe, registry/event-driven architecture with no direct polling.
- Cleaned generated caches and virtual environments from the release archive.

## 0.9.0 - Dashboard Foundation

- Added a versioned dashboard snapshot sensor with compact fleet and event data.
- Added a dependency-free Lovelace dashboard example using native cards.
- Kept the dashboard path push-driven and free of direct camera polling.
- Added dashboard schema tests and bilingual documentation.

## 0.8.0 - Home Assistant Event Bridge

- Subscribed only to discovered Tapo camera and binary-sensor entities.
- Normalized motion, person, vehicle, animal, crying, tamper, intrusion and line-crossing state changes.
- Added camera online/offline events from existing Home Assistant camera states.
- Added bounded in-memory event activity analytics and recent-event attributes.
- Added no polling, no database writes and no direct camera wake-up.

## 0.7.0 - Fleet Intelligence

- Added registry-only fleet analytics and a fleet quality grade.
- Added model, power-source, platform, entity-domain, and capability coverage summaries.
- Added a conservative attention list for cameras with incomplete evidence.
- Kept analysis local and passive: no network polling and no battery-camera wake-up.

## 0.6.0 - Capability Explorer

- Added a dedicated Capability Explorer sensor with one detailed profile per camera.
- Added evidence-labelled capability data without network polling or device wake-ups.
- Added per-camera power-source labels and registry-evidence health scores.
- Added average camera health and scan metadata to Home Assistant attributes.
- Kept identifiers privacy-safe and preserved unknown values instead of guessing.

## 0.5.1 - Official branding

- Added the official Tapo Event Bridge icon and logo.
- Added light and dark Home Assistant brand assets, including 2x variants.
- Added repository banner and icon assets.
- No runtime, polling, or camera behavior changes.

## 0.5.0 - Real Discovery

- Added live camera inventory attributes to the camera-count sensor.
- Added observed entity, capability, health, scan-time, and scan-duration sensors.
- Added per-camera entity-domain counts and enabled/disabled totals.
- Added discovery timing and error state to diagnostics export schema 2.
- Kept discovery registry-only: no network polling and no battery-camera wake-up.
- Included the Home Assistant runtime type-alias startup fix.

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
