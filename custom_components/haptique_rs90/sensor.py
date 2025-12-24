"""Sensor platform for Haptique RS90 Remote integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_REMOTE_ID
from .coordinator import HaptiqueRS90Coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Haptique RS90 sensor platform."""
    coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]
    entity_registry = er.async_get(hass)
    remote_id = entry.data[CONF_REMOTE_ID]
    
    # Base sensors (always present)
    entities = [
        RS90InfoSummarySensor(coordinator, entry),  # First for visibility
        HaptiqueRS90BatterySensor(coordinator, entry),
        HaptiqueRS90LastKeySensor(coordinator, entry),
        HaptiqueRS90RunningMacroSensor(coordinator, entry),
    ]
    
    # Track device command sensors by device ID
    device_sensors: dict[str, HaptiqueRS90DeviceCommandsSensor] = {}
    
    # Create device command sensors
    devices = coordinator.data.get("devices", [])
    device_id_to_name = {d.get("id"): d.get("name") for d in devices if d.get("id") and d.get("name")}
    sorted_devices = sorted(devices, key=lambda d: d.get("name", "").lower())
    
    for device in sorted_devices:
        device_id = device.get("id")
        device_name = device.get("name")
        if not device_id or not device_name:
            continue
        
        sensor = HaptiqueRS90DeviceCommandsSensor(coordinator, entry, device_name)
        device_sensors[device_id] = sensor
        entities.append(sensor)
        _LOGGER.debug("Setup commands sensor for device: %s (id: %s)", device_name, device_id)
    
    async_add_entities(entities)
    
    @callback
    def manage_device_sensors() -> None:
        """Add new device sensors and remove obsolete ones."""
        _LOGGER.debug("=== SENSOR: Entity update triggered ===")
        entity_registry = er.async_get(hass)
        
        # Build mapping of device IDs to names from current MQTT data
        current_devices = coordinator.data.get("devices", [])
        device_id_to_name = {device.get("id"): device.get("name") 
                            for device in current_devices 
                            if device.get("id") and device.get("name")}
        
        current_device_ids = set(device_id_to_name.keys())
        existing_device_ids = set(device_sensors.keys())
        
        _LOGGER.debug("Current device IDs from MQTT: %s", current_device_ids)
        _LOGGER.debug("Existing device IDs in HA: %s", existing_device_ids)
        
        # Check for renamed devices (same ID, different name)
        for device_id in current_device_ids & existing_device_ids:
            new_name = device_id_to_name[device_id]
            sensor = device_sensors.get(device_id)
            if sensor and sensor._device_name != new_name:
                old_name = sensor._device_name
                _LOGGER.info("RENAME: Device renamed: '%s' → '%s' (id: %s)", 
                            old_name, new_name, device_id)
                # Update sensor's internal name
                sensor._device_name = new_name
                # Update friendly name in entity registry
                entity_reg = er.async_get(hass)
                if entity_entry := entity_reg.async_get(sensor.entity_id):
                    entity_reg.async_update_entity(
                        sensor.entity_id,
                        name=f"Commands - {new_name}"
                    )
                # Force immediate state update
                sensor.async_write_ha_state()
                sensor.async_schedule_update_ha_state(force_refresh=True)
        
        # Find devices to add
        devices_to_add = current_device_ids - existing_device_ids
        new_entities = []
        
        if devices_to_add:
            _LOGGER.info("Devices to add (by ID): %s", devices_to_add)
        
        for device in coordinator.data.get("devices", []):
            device_id = device.get("id")
            device_name = device.get("name")
            if device_id in devices_to_add and device_name:
                sensor = HaptiqueRS90DeviceCommandsSensor(coordinator, entry, device_name)
                device_sensors[device_id] = sensor  # Use device_id as key, not name
                new_entities.append(sensor)
                _LOGGER.info("SUCCESS: Adding commands sensor for new device: %s (id: %s)", device_name, device_id)
        
        if new_entities:
            async_add_entities(new_entities)
        
        # Find devices to remove
        devices_to_remove = existing_device_ids - current_device_ids
        
        if devices_to_remove:
            _LOGGER.info("Devices to remove (by ID): %s", devices_to_remove)
        
        for device_id in devices_to_remove:
            sensor = device_sensors.pop(device_id, None)
            if sensor:
                device_name = sensor._device_name
                _LOGGER.debug("Processing removal of device: %s (id: %s, unique_id: %s)", 
                             device_name, device_id, sensor.unique_id)
                # Remove from entity registry
                entity_id = entity_registry.async_get_entity_id(
                    "sensor",
                    DOMAIN,
                    sensor.unique_id
                )
                if entity_id:
                    entity_registry.async_remove(entity_id)
                    _LOGGER.info("SUCCESS: Removed obsolete device commands sensor: %s (entity_id: %s)", 
                               device_name, entity_id)
                else:
                    _LOGGER.warning("Could not find entity_id for device sensor: %s (unique_id: %s)", 
                                   device_name, sensor.unique_id)
            else:
                _LOGGER.warning("Could not find sensor for device_id: %s", device_id)
    
    # Register listener for coordinator updates
    entry.async_on_unload(coordinator.async_add_listener(manage_device_sensors))


class HaptiqueRS90SensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Haptique RS90 sensors."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._remote_id = entry.data[CONF_REMOTE_ID]
        self._sensor_type = sensor_type
        self._attr_has_entity_name = True
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
        return f"{self._remote_id}_{self._sensor_type}"


class HaptiqueRS90BatterySensor(HaptiqueRS90SensorBase):
    """Battery level sensor for Haptique RS90."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator, entry, "battery")
        self._attr_name = "Battery"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        return self.coordinator.data.get("battery_level")

    @property
    def icon(self) -> str:
        """Return the icon based on battery level."""
        battery_level = self.native_value
        if battery_level is None:
            return "mdi:battery-unknown"
        if battery_level <= 10:
            return "mdi:battery-10"
        if battery_level <= 20:
            return "mdi:battery-20"
        if battery_level <= 30:
            return "mdi:battery-30"
        if battery_level <= 40:
            return "mdi:battery-40"
        if battery_level <= 50:
            return "mdi:battery-50"
        if battery_level <= 60:
            return "mdi:battery-60"
        if battery_level <= 70:
            return "mdi:battery-70"
        if battery_level <= 80:
            return "mdi:battery-80"
        if battery_level <= 90:
            return "mdi:battery-90"
        return "mdi:battery"


class HaptiqueRS90LastKeySensor(HaptiqueRS90SensorBase):
    """Last key pressed sensor for Haptique RS90."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the last key sensor."""
        super().__init__(coordinator, entry, "last_key")
        self._attr_name = "Last Key Pressed"
        self._attr_icon = "mdi:gesture-tap-button"

    @property
    def native_value(self) -> str | None:
        """Return the last key pressed."""
        last_key = self.coordinator.data.get("last_key")
        if last_key:
            return f"Button {last_key}"
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        last_key = self.coordinator.data.get("last_key")
        if last_key:
            return {"button_number": last_key}
        return {}


class HaptiqueRS90RunningMacroSensor(HaptiqueRS90SensorBase):
    """Running macro sensor for Haptique RS90."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the running macro sensor."""
        super().__init__(coordinator, entry, "running_macro")
        self._attr_name = "Running Macro"
        self._attr_icon = "mdi:play-circle"

    @property
    def native_value(self) -> str | None:
        """Return the running macro name or Idle."""
        # Get the macro that has status "on"
        macro_states = self.coordinator.data.get("macro_states", {})
        for macro_name, state in macro_states.items():
            if state == "on":
                return macro_name
        return "Idle"

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        if self.native_value and self.native_value != "Idle":
            return "mdi:play-circle"  # Icône play quand actif (sera coloré par HA)
        return "mdi:circle-outline"  # Icône vide quand idle

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        macro_states = self.coordinator.data.get("macro_states", {})
        return {
            "macro_states": macro_states,
            "active_macros": [name for name, state in macro_states.items() if state == "on"],
        }



class HaptiqueRS90DeviceCommandsSensor(HaptiqueRS90SensorBase):
    """Sensor for displaying commands of a specific device."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
        device_name: str,
    ) -> None:
        """Initialize the device commands sensor."""
        # Store device ID for stable unique_id and rename detection
        self._device_id = None
        for device in coordinator.data.get("devices", []):
            if device.get("name") == device_name:
                self._device_id = device.get("id")
                break
        
        if not self._device_id:
            _LOGGER.warning("Could not find device_id for device: %s", device_name)
            # Fallback: use sanitized name (old behavior)
            sanitized_name = device_name.lower()
            sanitized_name = sanitized_name.replace(' ', '_')
            sanitized_name = sanitized_name.replace('-', '_')
            sanitized_name = sanitized_name.replace('/', '_')
            sanitized_name = sanitized_name.replace('+', '_')
            sanitized_name = sanitized_name.replace('#', '_')
            sensor_type = f"commands_{sanitized_name}"
        else:
            # Use device_id in sensor_type for stable unique_id
            sensor_type = f"commands_{self._device_id}"
        
        super().__init__(coordinator, entry, sensor_type)
        
        # Store device name - friendly_name will come from @property name
        self._device_name = device_name
        
        self._attr_icon = "mdi:remote"
        # Catégorie diagnostic pour grouper séparément dans l'interface
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def name(self) -> str:
        """Return the friendly name (updates on rename)."""
        return f"Commands - {self._device_name}"

    @property
    def native_value(self) -> int:
        """Return the number of commands for this device."""
        commands = self.coordinator.data.get("device_commands", {}).get(self._device_name, [])
        return len(commands)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return command IDs as attributes."""
        commands = self.coordinator.data.get("device_commands", {}).get(self._device_name, [])
        command_ids = [cmd.get("id") for cmd in commands if cmd.get("id")]
        
        attributes = {
            "device_name": self._device_name,
            "rs90_device_id": self._device_id,  # Stable ID for service calls
            "command_count": len(commands),
            "commands": command_ids,  # List of all command IDs
        }
        
        # Add each command as a separate attribute for easy access
        for idx, cmd_id in enumerate(command_ids, 1):
            attributes[f"command_{idx}"] = cmd_id
        
        return attributes



class RS90InfoSummarySensor(HaptiqueRS90SensorBase):
    """Sensor providing RS90 configuration summary with all IDs."""
    
    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the RS90 info summary sensor."""
        super().__init__(coordinator, entry, "info_summary")
        
        self._attr_name = "Info Summary"
        self._attr_icon = "mdi:information-variant"
    
    @property
    def native_value(self) -> str:
        """Return summary state."""
        devices_count = len(self.coordinator.data.get("devices", []))
        macros_count = len(self.coordinator.data.get("macros", []))
        return f"{devices_count} devices, {macros_count} macros"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return all RS90 configuration information as attributes."""
        from homeassistant.helpers import device_registry as dr
        
        # Get RS90 device info from Home Assistant device registry
        device_registry = dr.async_get(self.hass)
        rs90_device = device_registry.async_get_device(
            identifiers={(DOMAIN, self._entry.data["remote_id"])}
        )
        
        ha_device_id = rs90_device.id if rs90_device else "N/A"
        
        # Build devices dictionary with name as key, id as value
        devices = self.coordinator.data.get("devices", [])
        devices_dict = {}
        for device in sorted(devices, key=lambda d: d.get("name", "").lower()):
            if device.get("name") and device.get("id"):
                devices_dict[device.get("name")] = device.get("id")
        
        # Build macros dictionary with name as key, id as value
        macros = self.coordinator.data.get("macros", [])
        macros_dict = {}
        for macro in sorted(macros, key=lambda m: m.get("name", "").lower()):
            if macro.get("name") and macro.get("id"):
                macros_dict[macro.get("name")] = macro.get("id")
        
        # RS90 info as individual attributes
        device_name = self._entry.data.get('name') or f"RS90 {self._entry.data['remote_id'][:8]}"
        
        return {
            # Devices with name: id format
            "devices": devices_dict,
            "devices_count": len(devices_dict),
            
            # Macros with name: id format
            "macros": macros_dict,
            "macros_count": len(macros_dict),
            
            # RS90 Remote info
            "rs90_id": ha_device_id,  # For service calls (HA device ID)
            "rs90_device_name": device_name,
        }

