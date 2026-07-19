# Tapo Event Bridge v1.1.0 — Native Event Journal

## ✨ Added

- Native **Event journal** sensor with newest events first
- Native camera filter select
- Native event-type filter select
- Compact event entries with camera, type, state, source, latency and confidence
- Recorder-safe payload capped at 25 displayed events

## 🔒 Data policy

- In-memory journal only
- No direct camera polling
- No forced battery-camera wake-up
- No extra database tables

## ✅ Quality

- Ruff checks passed
- Full Pytest suite passed
- JSON and Python compilation validated
- Explicit test keeps journal attributes below Home Assistant's 16 KiB Recorder limit

## 📦 Upgrade

1. Update through HACS
2. Restart Home Assistant
3. Open the Tapo Event Bridge device
4. Use **Journal camera filter** and **Journal event type filter**
5. Open **Event journal** to inspect the filtered entries
