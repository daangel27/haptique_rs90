"""Helpers for RS90 device commands.

Firmware 4.3 and older publish commands as ``{"id": "POWER", "name": "[ON, OFF]"}``
and can list the same ID twice. Firmware 4.4 publishes readable names
(``{"id": "ON", "name": "On"}``), splits grouped commands (POWER becomes ON and
OFF, MUTE_UNMUTE becomes MUTE and UNMUTE, PLAY_PAUSE becomes PLAY and PAUSE)
and gives toggle codes and duplicates a technical ID such as
``6adf6831cd975fa9bbfbb366`` with the name ``Power``.
"""

from __future__ import annotations

import re
from typing import Any

_TECHNICAL_ID = re.compile(r"^[0-9a-f]{24}$")

# 4.4 command IDs that replace a 4.3 ID, to keep saved dashboard selections.
LEGACY_IDS = {
    "ON": "POWER",
    "OFF": "POWER",
    "MUTE": "MUTE_UNMUTE",
    "UNMUTE": "MUTE_UNMUTE",
    "PLAY": "PLAY_PAUSE",
    "PAUSE": "PLAY_PAUSE",
}


def is_technical_id(command_id: str | None) -> bool:
    """True for IDs the firmware generates, e.g. 6adf6831cd975fa9bbfbb366."""
    return bool(command_id) and bool(_TECHNICAL_ID.match(str(command_id)))


def _readable_name(name: Any) -> str | None:
    """The command name, unless it is a 4.3 list such as "[ON, OFF]"."""
    if not isinstance(name, str):
        return None
    name = name.strip()
    if not name or (name.startswith("[") and name.endswith("]")):
        return None
    return name


def command_key(command: dict[str, Any]) -> str:
    """Symbolic key used for icons and layout, e.g. POWER, VOLUME_UP, OK.

    Technical IDs carry no meaning, so the key comes from the name:
    "Power" -> POWER, "Volume +" -> VOLUME_UP, "Mute/Unmute" -> MUTE_UNMUTE.
    """
    command_id = str(command.get("id") or "")
    if not is_technical_id(command_id):
        return command_id
    name = _readable_name(command.get("name")) or command_id
    name = name.replace("+", " UP").replace("-", " DOWN")
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_") or command_id


def command_label(command: dict[str, Any]) -> str:
    """Text shown to the user: the readable name, else the ID."""
    name = _readable_name(command.get("name"))
    if name:
        # Some codes come all lowercase ("hdmi out 1"): capitalise the first letter.
        return name[0].upper() + name[1:] if name == name.lower() else name
    return str(command.get("id") or "").replace("_", " ")


def unique_commands(commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Commands with an ID, without duplicate IDs, with a key and a label.

    Two commands with the same name (4.4 keeps both, with their own ID) get
    "2", "3"… after the name so the buttons can be told apart.
    """
    seen: set[str] = set()
    labels: dict[str, int] = {}
    result = []
    for command in commands:
        command_id = command.get("id")
        if not command_id or command_id in seen:
            continue
        seen.add(command_id)
        label = command_label(command)
        count = labels.get(label.lower(), 0) + 1
        labels[label.lower()] = count
        result.append(
            {
                "id": command_id,
                "name": command.get("name"),
                "key": command_key(command),
                "label": label if count == 1 else f"{label} {count}",
            }
        )
    return result


def is_selected(command: dict[str, Any], chosen: list[str]) -> bool:
    """Whether a saved selection includes the command.

    Selections saved with firmware 4.3 hold IDs that 4.4 renamed: POWER still
    selects ON, OFF and the "Power" toggle.
    """
    command_id = command.get("id")
    return (
        command_id in chosen
        or command_key(command) in chosen
        or LEGACY_IDS.get(str(command_id)) in chosen
    )


def find_command(
    commands: list[dict[str, Any]], command_id: str
) -> dict[str, Any] | None:
    """The command with this ID, if the device lists it."""
    return next((c for c in commands if c.get("id") == command_id), None)
