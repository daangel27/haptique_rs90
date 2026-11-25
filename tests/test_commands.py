"""Device commands published by firmware 4.3 and 4.4."""

from custom_components.haptique_rs90.commands import (
    command_key,
    command_label,
    is_selected,
    is_technical_id,
    unique_commands,
)
from custom_components.haptique_rs90.logbook import command_icon

# AMPLI as published by firmware 4.4 (build 94), shortened.
AMPLI_44 = [
    {"id": "ON", "name": "On"},
    {"id": "OFF", "name": "Off"},
    {"id": "6adf6831cd975fa9bbfbb366", "name": "Power"},
    {"id": "VOLUME_UP", "name": "Volume +"},
    {"id": "MUTE", "name": "Mute"},
    {"id": "UNMUTE", "name": "Unmute"},
    {"id": "6adf6831cd975fa9bbfbb371", "name": "Mute/Unmute"},
    {"id": "INPUT_CBL_SAT", "name": "input cbl/sat"},
]

# CANALSAT keeps two codes with the same name, each with its own ID.
CANALSAT_44 = [
    {"id": "6aecfb1c522dcdf44369a1a9", "name": "Volume +"},
    {"id": "6aecfb27522dcdf44369a20a", "name": "Volume +"},
    {"id": "6aecfb1c522dcdf44369a1ab", "name": "Volume -"},
]

# Firmware 4.3: names are lists and IDs can be duplicated.
AMPLI_43 = [
    {"id": "POWER", "name": "[ON, OFF]"},
    {"id": "POWER", "name": "[POWER]"},
    {"id": "MUTE_UNMUTE", "name": "[MUTE, UNMUTE]"},
]


def test_technical_ids():
    assert is_technical_id("6adf6831cd975fa9bbfbb366")
    assert not is_technical_id("POWER")
    assert not is_technical_id("0")
    assert not is_technical_id(None)


def test_keys_and_labels_44():
    commands = {c["id"]: c for c in unique_commands(AMPLI_44)}
    power = commands["6adf6831cd975fa9bbfbb366"]
    assert (power["key"], power["label"]) == ("POWER", "Power")
    toggle = commands["6adf6831cd975fa9bbfbb371"]
    assert (toggle["key"], toggle["label"]) == ("MUTE_UNMUTE", "Mute/Unmute")
    assert commands["ON"]["label"] == "On"
    assert commands["VOLUME_UP"]["key"] == "VOLUME_UP"
    assert commands["INPUT_CBL_SAT"]["label"] == "input cbl/sat"


def test_same_name_gets_a_number():
    commands = unique_commands(CANALSAT_44)
    assert [c["key"] for c in commands] == ["VOLUME_UP", "VOLUME_UP", "VOLUME_DOWN"]
    assert [c["label"] for c in commands] == ["Volume +", "Volume + 2", "Volume -"]


def test_firmware_43_unchanged():
    commands = unique_commands(AMPLI_43)
    assert [c["id"] for c in commands] == ["POWER", "MUTE_UNMUTE"]
    assert [c["label"] for c in commands] == ["POWER", "MUTE UNMUTE"]
    assert command_key({"id": "POWER", "name": "[POWER]"}) == "POWER"
    assert command_label({"id": "PLAY_PAUSE"}) == "PLAY PAUSE"


def test_selection_saved_with_43_still_matches():
    saved = ["POWER", "MUTE_UNMUTE", "VOLUME_UP"]
    chosen = [c["id"] for c in unique_commands(AMPLI_44) if is_selected(c, saved)]
    assert chosen == [
        "ON",
        "OFF",
        "6adf6831cd975fa9bbfbb366",
        "VOLUME_UP",
        "MUTE",
        "UNMUTE",
        "6adf6831cd975fa9bbfbb371",
    ]


def test_logbook_icons():
    assert command_icon("ON") == "mdi:power"
    assert command_icon("OFF") == "mdi:power"
    assert command_icon("UNMUTE") == "mdi:volume-high"
    assert command_icon("PLAY") == "mdi:play"
    assert command_icon("PLAY_PAUSE") == "mdi:play-pause"
