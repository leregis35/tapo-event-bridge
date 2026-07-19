# Home Assistant Event Bridge

Version 0.8.0 listens only to the already existing Home Assistant entities attached to discovered Tapo cameras. Meaningful state transitions are normalized into Tapo Event Bridge events.

The listener is scoped to known entity IDs, uses no polling, writes no database records, and does not contact or wake cameras directly. The Event activity sensor exposes bounded in-memory counts, active detections, and the latest 20 events.
