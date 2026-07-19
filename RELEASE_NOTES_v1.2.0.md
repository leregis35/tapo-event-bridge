# 🎛️ Tapo Event Bridge v1.2.0

## Fleet Command Center

This release adds a compact, Recorder-safe supervision view for the entire Tapo camera fleet.

## ✨ Added

- New **Fleet command center** sensor
- Per-camera live activity summaries
- Latest event with camera name, event type, state and time
- Most active camera calculation
- Active detection count across the fleet
- Event-type distribution
- Camera health, model and power-source overview
- Cameras requiring attention
- Stable `schema_version: 1` payload for Lovelace

## 🛡 Resource policy

- No direct camera polling
- No forced battery-camera wake-up
- Bounded in-memory event analysis
- Recorder-safe attributes, capped at 12 camera summaries

## ✅ Quality

- Ruff checks passed
- Full Pytest suite passed
- Home Assistant JSON and Python validation passed
