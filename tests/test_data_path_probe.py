from custom_components.tapo_event_bridge.data_path_probe import build_data_path_entry


def test_build_data_path_entry_captures_candidate_attribute_diff() -> None:
    entry = build_data_path_entry(
        camera_id="camera-test",
        camera_name="Carport",
        entity_id="sensor.carport_last_alarm",
        old_state="idle",
        new_state="person",
        old_attributes={"last_alarm": "none"},
        new_attributes={"last_alarm": "person"},
    )
    assert entry is not None
    assert "person" in entry["candidate_tokens"]
    assert entry["changed_attributes"]["last_alarm"]["new"] == "person"


def test_build_data_path_entry_ignores_identical_update() -> None:
    assert build_data_path_entry(
        camera_id="camera-test",
        camera_name="Carport",
        entity_id="sensor.carport_rssi",
        old_state="-60",
        new_state="-60",
        old_attributes={"unit_of_measurement": "dBm"},
        new_attributes={"unit_of_measurement": "dBm"},
    ) is None
