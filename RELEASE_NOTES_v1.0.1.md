# 🛠 Tapo Event Bridge v1.0.1

## Recorder-safe Capability Explorer

This stabilization release fixes a Home Assistant Recorder warning caused by oversized Capability Explorer state attributes.

## Fixed

- Reduced Capability Explorer state attributes below Home Assistant's 16 KiB Recorder limit.
- Prevented verbose evidence metadata from being written on every state update.
- Added deterministic bounds for large camera fleets and long capability lists.

## Preserved

- Full per-camera evidence remains available through **Download diagnostics**.
- Camera discovery remains registry-only, with no direct camera polling.
- Battery cameras are not awakened by this integration.

## Validation

- Ruff checks passed
- Full Pytest suite passed
- JSON and Python compilation validated
- Regression coverage added for Recorder payload size

## Upgrade

Update through HACS and restart Home Assistant. The previous Recorder warning should no longer return after the Capability Explorer updates.
