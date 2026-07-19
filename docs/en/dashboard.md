# Dashboard foundation

Version 0.9.0 adds `sensor.tapo_event_bridge_dashboard_snapshot`. Its state is the fleet grade and its attributes expose a versioned, compact schema for Lovelace.

The included example dashboard uses only built-in Home Assistant cards. It reads existing native entities and does not poll cameras. Copy `docs/lovelace/tapo_event_bridge_dashboard.yaml` into a manual dashboard or use it as a starting point.
