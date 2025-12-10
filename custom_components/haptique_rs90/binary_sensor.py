"""Binary sensor platform for Haptique RS90 Remote integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_REMOTE_ID, STATE_ONLINE
from .coordinator import HaptiqueRS90Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Haptique RS90 binary sensor platform."""
    coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        HaptiqueRS90ConnectionSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class HaptiqueRS90ConnectionSensor(CoordinatorEntity, BinarySensorEntity):
    """Connection status sensor for Haptique RS90."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the connection sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._remote_id = entry.data[CONF_REMOTE_ID]
        self._attr_has_entity_name = True
        self._attr_name = "Connection"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._remote_id)},
            "name": entry.data.get("name", f"Haptique RS90 {self._remote_id[:8]}"),
            "manufacturer": "Haptique",
            "model": "RS90",
            "sw_version": "1.0",
        }

    @property
    def unique_id(self) -> str:
        """Return unique ID for the sensor."""
        return f"{self._remote_id}_connection"

    @property
    def is_on(self) -> bool:
        """Return true if the remote is online."""
        return self.coordinator.data.get("status") == STATE_ONLINE

    @property
    def icon(self) -> str:
        """Return icon based on connection state."""
        if self.is_on:
            return "mdi:connection"  # Connecté - icône sera colorée en vert par HA
        return "mdi:close-network-outline"  # Déconnecté - icône sera colorée en rouge par HA

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # This sensor is always available as it tracks connection status
        return True
