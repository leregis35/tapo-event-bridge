# 💡 Tapo Event Bridge v1.3.0 — Person Lighting Bridge

This release delivers the original project goal: turning on camera LEDs or floodlights when a human is detected.

## Added

- Opt-in **Person detection lighting** switch
- Automatic same-device mapping between Tapo cameras and Home Assistant light entities
- Configurable light-on duration from 10 to 900 seconds
- Timer reset when another person event arrives
- Person-lighting status, mapped targets, trigger count and last trigger diagnostics

## Safety and efficiency

- Disabled by default to prevent unexpected actuation
- Uses existing Home Assistant person events and light services
- Ignores replayed events
- No direct camera polling
- No battery camera wake-up

## Validation

- Ruff passed
- Pytest passed
- Home Assistant JSON and Python compilation validated

## Upgrade

Update through HACS, restart Home Assistant, then enable **Person detection lighting**.
