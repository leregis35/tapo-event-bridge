# Tapo Event Bridge v1.6.1 — Signal Integrity

This maintenance release turns the v1.6 data-path probe into a camera-only,
low-noise diagnostic tool.

## Changes

- Tracks only entities provided by `tapo_control`.
- Excludes unrelated devices and Tapo Event Bridge's own entities.
- Candidate matching no longer scans entity IDs, eliminating false matches from
  names containing `event`, `person`, or `trigger`.
- Adds `candidate_by_camera` and a clear `signal_verdict` to the probe report.
- Keeps the probe opt-in, bounded, in-memory, and free of direct camera polling.

## Important finding

Tapo: Cameras Control documents that motion events require ONVIF. Battery and
solar devices generally do not expose ONVIF, so C425/C660 motion events cannot
be assumed to exist in Home Assistant. This release reports that limitation
cleanly instead of manufacturing candidate events from unrelated state changes.
