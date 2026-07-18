# Event engine

Tapo Event Bridge uses a transport-neutral `CameraEvent` model. Event sources
will publish into one low-overhead engine instead of exposing protocol-specific
payloads to Home Assistant platforms.

The recorder is bounded and memory-only. Replay creates sanitized copies and
never republishes raw camera payloads. No polling or background task is started.
