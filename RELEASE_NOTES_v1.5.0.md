# Tapo Event Bridge v1.5.0 — Camera State Probe

## Added

- Opt-in camera state-change diagnostic mode
- Exact camera and entity attribution for every captured Home Assistant state change
- Bounded in-memory probe report with recent changes and per-camera/domain counters
- Clear state-change probe button

## Scope and privacy

This release observes only Home Assistant state changes for entities already associated with discovered cameras. It does not sniff network traffic, poll cameras, or force battery cameras to wake.

## Test procedure

1. Enable **State-change diagnostic mode**.
2. Clear the probe.
3. Trigger one camera only.
4. Open **Camera state-change probe** and inspect `recent_changes`.
5. Disable the mode after testing.
