# Fleet command center

The Fleet command center sensor provides one compact overview of the complete camera fleet. It combines registry-based camera information with normalized Home Assistant events already observed by Tapo Event Bridge.

Its attributes include fleet health, active detections, event distribution, the most active camera, the latest event and one bounded summary per camera.

The payload is intentionally limited to 12 camera summaries so Home Assistant Recorder can store it safely. Full low-level evidence remains available from integration diagnostics.
