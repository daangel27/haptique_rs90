"""RS90 settings with a list of values (firmware 4.4+)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .settings import SELECT_SETTINGS, HaptiqueRS90Setting, add_when_published


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    add_when_published(
        coordinator,
        entry,
        SELECT_SETTINGS,
        lambda name: HaptiqueRS90SettingSelect(coordinator, entry, name),
        async_add_entities,
    )


class HaptiqueRS90SettingSelect(HaptiqueRS90Setting, SelectEntity):
    """E.g. Stay ready: how long the RS90 stays reachable before deep sleep."""

    def __init__(self, coordinator, entry, name) -> None:
        super().__init__(coordinator, entry, name)
        self._attr_icon, self._known = SELECT_SETTINGS[name]

    @property
    def options(self) -> list[str]:
        # A value the firmware adds later is shown too, as published.
        value = self.value
        return self._known + ([value] if value and value not in self._known else [])

    @property
    def current_option(self) -> str | None:
        return self.value

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_setting(self._setting, option)
