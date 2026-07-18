# Tapo Event Bridge

Experimental Home Assistant custom integration for discovering the event path used by TP-Link Tapo cameras, especially battery models such as C425 and C660.

## Version 0.1.0: passive probe

This first release is intentionally conservative:

- it does **not** connect to any camera;
- it does **not** authenticate to TP-Link cloud;
- it does **not** open a video stream;
- it does **not** wake battery cameras;
- it passively watches Home Assistant's event bus for camera/detection candidates;
- it stores only redacted in-memory diagnostics;
- it includes a synthetic test event to validate the plumbing.

This release will not yet solve battery-camera detection by itself. Its purpose is to validate the Home Assistant side safely before implementing a documented and testable Tapo event transport.

## Manual installation

Copy:

```text
custom_components/tapo_event_bridge
```

to:

```text
/config/custom_components/tapo_event_bridge
```

Restart Home Assistant, then add **Tapo Event Bridge** from:

```text
Settings → Devices & services → Add integration
```

## Test

Run action:

```yaml
action: tapo_event_bridge.inject_test_event
data:
  camera: carport
  type: people_detection
```

Expected result:

- `sensor.tapo_event_bridge_candidate_event_count` increases;
- `sensor.tapo_event_bridge_last_candidate_event` becomes `tapo_test_person_detected`;
- diagnostics contain the redacted synthetic event.

## Real-world capture test

After setup, walk in front of a camera and wait for a Tapo notification. Then download diagnostics from the integration menu. If no candidate appears, that confirms the alert is not already entering Home Assistant's event bus and the next milestone must implement a dedicated Tapo cloud/push transport.

## Security

Do not publish raw Home Assistant logs. Diagnostics are redacted, but review them before sharing.

## Roadmap

- 0.1: passive event-bus probe
- 0.2: transport research and raw-event adapter interface
- 0.3: opt-in cloud authentication prototype, only if a safe event endpoint is verified
- 0.4: person/motion/vehicle/pet event entities
- 1.0: stable HACS release with tests and documentation

## Trademark

Tapo and TP-Link are trademarks of their respective owners. This community project is not affiliated with or endorsed by TP-Link.
