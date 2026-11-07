"""Describe Haptique RS90 execution results in the logbook.

Also describes device commands sent and wake-ups.

The Last Macro Result sensor only creates a logbook entry when its state
changes, so repeated identical results (e.g. two consecutive "skipped") would
be invisible. Every result event gets its own entry here instead.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.logbook import (
    LOGBOOK_ENTRY_ENTITY_ID,
    LOGBOOK_ENTRY_ICON,
    LOGBOOK_ENTRY_MESSAGE,
    LOGBOOK_ENTRY_NAME,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import COMMAND_EVENT, DOMAIN, WAKE_EVENT
from .targets import RESULT_EVENT


def result_message(data: dict[str, Any]) -> str:
    """Build a short message such as 'OFF: skipped (already_in_requested_state)'."""
    status = data.get("status") or "unknown"
    if error := data.get("error"):
        status = f"{status} ({error})"
    action = data.get("action")
    prefix = action.upper() if action else "result"
    return f"{prefix}: {status}"


# First matching prefix wins; checked on the upper-cased command name.
_COMMAND_ICONS = (
    ("POWER", "mdi:power"),
    ("VOLUME_UP", "mdi:volume-plus"),
    ("VOL_UP", "mdi:volume-plus"),
    ("VOLUME_DOWN", "mdi:volume-minus"),
    ("VOL_DOWN", "mdi:volume-minus"),
    ("MUTE", "mdi:volume-mute"),
    ("CHANNEL", "mdi:television-guide"),
    ("CH_", "mdi:television-guide"),
    ("UP", "mdi:arrow-up-bold"),
    ("DOWN", "mdi:arrow-down-bold"),
    ("LEFT", "mdi:arrow-left-bold"),
    ("RIGHT", "mdi:arrow-right-bold"),
    ("OK", "mdi:checkbox-blank-circle-outline"),
    ("SELECT", "mdi:checkbox-blank-circle-outline"),
    ("ENTER", "mdi:checkbox-blank-circle-outline"),
    ("RETURN", "mdi:keyboard-return"),
    ("BACK", "mdi:keyboard-return"),
    ("HOME", "mdi:home"),
    ("MENU", "mdi:menu"),
    ("INFO", "mdi:information-outline"),
    ("PLAY", "mdi:play-pause"),
    ("PAUSE", "mdi:pause"),
    ("STOP", "mdi:stop"),
    ("REWIND", "mdi:rewind"),
    ("FAST_FORWARD", "mdi:fast-forward"),
    ("FORWARD", "mdi:fast-forward"),
    ("INPUT", "mdi:import"),
    ("SOURCE", "mdi:import"),
)

_WAKE_ICONS = {"sent": "mdi:alarm", "woke": "mdi:alarm-check"}


# Same arrow as Home Assistant's own "state → new state" entries.
ARROW = "→ "


def command_icon(command: str | None) -> str:
    """Pick an icon for a device command, e.g. mdi:power for POWER_OFF."""
    name = (command or "").upper()
    if name.isdigit():
        return "mdi:dialpad"
    for prefix, icon in _COMMAND_ICONS:
        if name.startswith(prefix):
            return icon
    return "mdi:remote"


def wake_message(data: dict[str, Any]) -> str:
    """Build a message such as 'woke up in 18 s'."""
    result = data.get("result")
    if result == "sent":
        return "wake-up sent"
    seconds = data.get("seconds")
    if result == "woke":
        return f"woke up in {seconds} s"
    return f"did not wake up within {seconds} s"


def _target_entity_id(
    hass: HomeAssistant, remote_id: str, kind: str, target_id: str
) -> str | None:
    """Find the switch of a macro/sequence, including migrated identities."""
    registry = er.async_get(hass)
    # Migrated legacy sequences keep the old "macro" identity, and a real
    # macro whose ID collided with one uses "real_macro" (see switch.py).
    identities = [kind, "real_macro" if kind == "macro" else "macro"]
    for identity in identities:
        entity_id = registry.async_get_entity_id(
            "switch", DOMAIN, f"{remote_id}_{identity}_{target_id}"
        )
        if not entity_id:
            continue
        entry = registry.async_get(entity_id)
        owner = (
            (entry.capabilities or {}).get("haptique_target_kind") if entry else None
        )
        if owner == kind or (owner is None and identity == kind):
            return entity_id
    return None


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[[str, str, Callable[[Event], dict[str, str]]], None],
) -> None:
    """Register the result event description."""

    @callback
    def async_describe_result(event: Event) -> dict[str, str]:
        data = event.data
        name = data.get("target_name") or data.get("target_id") or "RS90"
        description = {
            LOGBOOK_ENTRY_NAME: f"RS90 {name}",
            LOGBOOK_ENTRY_MESSAGE: ARROW + result_message(data),
        }
        # Attach the entry to the macro/sequence switch so it also shows up
        # in that entity's own logbook.
        remote_id = data.get("remote_id")
        kind = data.get("target_kind")
        target_id = data.get("target_id")
        if remote_id and kind and target_id:
            if entity_id := _target_entity_id(hass, remote_id, kind, target_id):
                description[LOGBOOK_ENTRY_ENTITY_ID] = entity_id
        return description

    async_describe_event(DOMAIN, RESULT_EVENT, async_describe_result)

    @callback
    def async_describe_command(event: Event) -> dict[str, str]:
        data = event.data
        return {
            LOGBOOK_ENTRY_NAME: f"RS90 {data.get('device') or 'device'}",
            LOGBOOK_ENTRY_MESSAGE: f"{ARROW}{data.get('command')} sent",
            LOGBOOK_ENTRY_ICON: command_icon(data.get("command")),
        }

    async_describe_event(DOMAIN, COMMAND_EVENT, async_describe_command)

    @callback
    def async_describe_wake(event: Event) -> dict[str, str]:
        return {
            LOGBOOK_ENTRY_NAME: "RS90",
            LOGBOOK_ENTRY_MESSAGE: ARROW + wake_message(event.data),
            LOGBOOK_ENTRY_ICON: _WAKE_ICONS.get(
                event.data.get("result"), "mdi:alarm-off"
            ),
        }

    async_describe_event(DOMAIN, WAKE_EVENT, async_describe_wake)
