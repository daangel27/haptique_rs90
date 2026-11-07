"""Button platform for Haptique RS90 Remote integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_REMOTE_ID, DOMAIN
from .coordinator import HaptiqueRS90Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Haptique RS90 button platform."""
    coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        HaptiqueRS90RGBButton(coordinator, entry),
        HaptiqueRS90RefreshButton(coordinator, entry),
        HaptiqueRS90WakeButton(coordinator, entry),
    ]

    async_add_entities(entities)

    apps: dict[str, HaptiqueRS90AppButton] = {}

    @callback
    def reconcile_apps():
        additions = []
        for app in coordinator.data["apps"]:
            package_id = app["id"]
            if package_id not in apps:
                button = HaptiqueRS90AppButton(
                    coordinator, entry, package_id, app["name"]
                )
                apps[package_id] = button
                additions.append(button)
            else:
                apps[package_id]._app_name = app["name"]
        if additions:
            async_add_entities(additions)

    reconcile_apps()
    entry.async_on_unload(coordinator.async_add_listener(reconcile_apps))


class HaptiqueRS90RefreshButton(CoordinatorEntity, ButtonEntity):
    """Ask the RS90 to publish its devices, macros, sequences and apps again."""

    _attr_has_entity_name = True
    _attr_translation_key = "refresh_lists"
    _attr_icon = "mdi:sync"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: HaptiqueRS90Coordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        remote_id = entry.data[CONF_REMOTE_ID]
        self._attr_unique_id = f"{remote_id}_refresh_lists"
        self._attr_device_info = {"identifiers": {(DOMAIN, remote_id)}}

    @property
    def available(self) -> bool:
        return self.coordinator.data.get("status") == "online"

    async def async_press(self) -> None:
        await self.coordinator.async_force_refresh_lists()


class HaptiqueRS90WakeButton(CoordinatorEntity, ButtonEntity):
    """Wake a sleeping RS90 up (needs its IP address in the options)."""

    _attr_has_entity_name = True
    _attr_translation_key = "wake"
    _attr_icon = "mdi:alarm"

    def __init__(
        self, coordinator: HaptiqueRS90Coordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        remote_id = entry.data[CONF_REMOTE_ID]
        self._attr_unique_id = f"{remote_id}_wake"
        self._attr_device_info = {"identifiers": {(DOMAIN, remote_id)}}

    @property
    def available(self) -> bool:
        return self.coordinator.wake_host is not None

    async def async_press(self) -> None:
        await self.coordinator.async_wake()


class HaptiqueRS90RGBButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger RGB Ring Light animation."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the RGB button."""
        super().__init__(coordinator)
        self._entry = entry
        self._remote_id = entry.data[CONF_REMOTE_ID]

        # Entity configuration
        self._attr_has_entity_name = True
        self._attr_name = "RGB Ring Light"
        self._attr_unique_id = f"{self._remote_id}_rgb_button"
        self._attr_icon = "mdi:lightbulb-on"

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._remote_id)},
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get("status") == "online"

    async def async_press(self) -> None:
        """Handle button press - trigger RGB with default 5 seconds."""
        _LOGGER.debug("RGB Ring Light button pressed (default 5 seconds)")
        await self.coordinator.async_control_led_light("on", duration=5)


class HaptiqueRS90AppButton(CoordinatorEntity, ButtonEntity):
    """Launch by package ID and expose the last firmware launch outcome."""

    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry, package_id: str, app_name: str) -> None:
        super().__init__(coordinator)
        self._package_id = package_id
        self._app_name = app_name
        self._attr_unique_id = f"{entry.data[CONF_REMOTE_ID]}_app_{package_id}"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:application"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.data[CONF_REMOTE_ID])}}

    @property
    def name(self) -> str:
        return self._app_name

    @property
    def available(self) -> bool:
        awake = self.coordinator.data["status"] == "online" or self.coordinator.auto_wake
        return awake and self._package_id in {
            item["id"] for item in self.coordinator.data["apps"]
        }

    @property
    def extra_state_attributes(self):
        return {
            "app_package_id": self._package_id,
            "app_name": self._app_name,
            "last_result": self.coordinator.data["app_results"].get(self._package_id),
        }

    async def async_press(self) -> None:
        await self.coordinator.async_launch_app(self._package_id)
