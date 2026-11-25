"""RS90 settings published over MQTT by firmware 4.4 and later.

The RS90 publishes each setting retained on ``settings/<name>`` and accepts a
new value on ``settings/<name>/set``. An entity is only created once its topic
has been seen, so nothing appears with older firmware.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_REMOTE_ID, DOMAIN
from .coordinator import HaptiqueRS90Coordinator

# On/off settings shown as switches: name -> icon
SWITCH_SETTINGS = {
    "autodisplay": "mdi:cellphone-arrow-down",
    "backlight": "mdi:keyboard-outline",
}

# Settings with a list of values shown as selects: name -> (icon, known values)
SELECT_SETTINGS = {
    "stay_ready": ("mdi:timer-sand", ["5", "30", "always"]),
}


class HaptiqueRS90Setting(CoordinatorEntity):
    """Base for an RS90 setting entity."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: HaptiqueRS90Coordinator, entry: ConfigEntry, name: str
    ) -> None:
        super().__init__(coordinator)
        remote_id = entry.data[CONF_REMOTE_ID]
        self._setting = name
        self._attr_translation_key = name
        self._attr_unique_id = f"{remote_id}_setting_{name}"
        self._attr_device_info = {"identifiers": {(DOMAIN, remote_id)}}

    @property
    def value(self) -> str | None:
        return self.coordinator.data.get("settings", {}).get(self._setting)

    @property
    def available(self) -> bool:
        return self.value is not None and (
            self.coordinator.data.get("status") == "online"
            or self.coordinator.auto_wake
        )


def add_when_published(
    coordinator: HaptiqueRS90Coordinator,
    entry: ConfigEntry,
    names: Iterable[str],
    factory: Callable[[str], Entity],
    async_add_entities: Callable[[list[Entity]], None],
) -> None:
    """Create each setting entity the first time its topic is received."""
    added: set[str] = set()
    names = list(names)

    @callback
    def reconcile() -> None:
        published = coordinator.data.get("settings", {})
        new = [name for name in names if name in published and name not in added]
        if new:
            added.update(new)
            async_add_entities([factory(name) for name in new])

    reconcile()
    entry.async_on_unload(coordinator.async_add_listener(reconcile))
