# Tapo Event Bridge 1.6.0 — Data Path Instrumentation

This diagnostic release adds an opt-in, bounded view of the Home Assistant data path used by discovered Tapo camera entities.

## Added
- Explicit startup/setup logging under `custom_components.tapo_event_bridge`.
- Camera data-path probe switch, sensor and clear button.
- State **and selected attribute** diffs for entities attached to discovered Tapo camera devices.
- Candidate-token tagging for person, motion, alarm, event, PIR, ring and detection-related updates.
- Privacy-safe entity identifiers and bounded in-memory retention.

## Fixed
- The state-probe clear button remains available even when the probe is empty.

## Scope
This release instruments observable Home Assistant entity updates. It does not sniff network traffic, expose credentials or patch `tapo_control` internals.
