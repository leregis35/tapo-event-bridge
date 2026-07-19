# 🔎 Tapo Event Bridge v1.4.0 — Source Resolution Engine

## Highlights

- Camera identity is now preserved for every normalized event.
- “Last event source” now displays the actual camera name.
- New transport and combined camera/event sensors.
- Improved C660 and C425 floodlight association, including sibling-device entities.
- Unmapped person events are recorded for troubleshooting.

## Why this matters

Person lighting can only be reliable when the bridge knows exactly which camera generated the event. This release fixes that missing link before further automation work.

## Quality

- Ruff validated
- Pytest validated
- No direct camera polling
- No forced battery-camera wake-up
