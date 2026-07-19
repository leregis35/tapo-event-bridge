# 🚀 Tapo Event Bridge v1.0.0

## Production Foundation

Version 1.0 marks the first stable Tapo Event Bridge release and locks the
version-1 dashboard and diagnostics contract.

## ✨ Highlights

- Stable dashboard payload schema version 1
- Duplicate suppression for noisy Home Assistant state transitions
- Runtime uptime, buffer and transport telemetry
- Clear in-memory event history diagnostic action
- Registry-only, battery-safe camera discovery
- Bounded event memory with no integration database writes
- Native Home Assistant event bus publishing
- Official project branding and HACS distribution workflow

## 🆕 Added

- **Runtime metrics** sensor
- **Clear event history** button
- Duplicate-event counter and configurable engine window
- Runtime listener, cleanup and active-transport telemetry
- English and French version-1 documentation

## 🛡 Stability and privacy

- No direct camera polling
- No intentional battery-camera wake-up
- No raw payload in replayed events
- No Home Assistant Recorder deletion from the clear-history action
- Privacy-safe camera and entity identifiers in exported data

## ✅ Validation

- Ruff: passed
- Pytest: 56 tests passed
- Python compilation: passed
- JSON translations and manifest: valid
- Home Assistant/HACS upgrade workflow ready for field validation

## 📦 Upgrade

1. Update Tapo Event Bridge through HACS.
2. Restart Home Assistant.
3. Confirm version `1.0.0` and the new entities.
4. Test real camera events before enabling production automations.
