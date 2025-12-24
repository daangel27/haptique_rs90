"""The Haptique RS90 Remote integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import HaptiqueRS90Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.LIGHT,   # RGB ring light control - First in controls section
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,  # Macros as switches (on/off state visible)
]


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Haptique RS90."""
    
    async def handle_trigger_macro(call):
        """Handle the trigger_macro service call."""
        rs90_id = call.data.get("rs90_id")
        rs90_macro_id = call.data.get("rs90_macro_id")
        action = call.data.get("action", "on")  # Default to "on"
        
        if not rs90_macro_id:
            _LOGGER.error("rs90_macro_id is required")
            return
        
        # Find the coordinator for this device
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(rs90_id)
        
        if not device_entry:
            _LOGGER.error("Device not found: %s", rs90_id)
            return
        
        # Find the config entry
        for entry_id in device_entry.config_entries:
            if entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN][entry_id]
                
                # Resolve rs90_macro_id to macro_name (for MQTT topic)
                macros = coordinator.data.get("macros", [])
                macro_name = None
                for macro in macros:
                    if macro.get("id") == rs90_macro_id:
                        macro_name = macro.get("name")
                        _LOGGER.debug("Resolved rs90_macro_id %s to macro_name: %s", 
                                    rs90_macro_id, macro_name)
                        break
                
                if not macro_name:
                    _LOGGER.error("Could not find macro with rs90_macro_id: %s", rs90_macro_id)
                    return
                
                await coordinator.async_trigger_macro(macro_name, action)
                return
        
        _LOGGER.error("Coordinator not found for device: %s", rs90_id)
    
    async def handle_trigger_device_command(call):
        """Handle the trigger_device_command service call."""
        rs90_id = call.data.get("rs90_id")
        rs90_device_id = call.data.get("rs90_device_id")
        command_name = call.data.get("command_name")
        
        if not rs90_device_id:
            _LOGGER.error("rs90_device_id is required")
            return
        
        # Find the coordinator for this device
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(rs90_id)
        
        if not device_entry:
            _LOGGER.error("Device not found: %s", rs90_id)
            return
        
        # Find the config entry
        for entry_id in device_entry.config_entries:
            if entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN][entry_id]
                
                # Resolve rs90_device_id to device_name (for MQTT topic)
                devices = coordinator.data.get("devices", [])
                device_name = None
                for device in devices:
                    if device.get("id") == rs90_device_id:
                        device_name = device.get("name")
                        _LOGGER.debug("Resolved rs90_device_id %s to device_name: %s", 
                                    rs90_device_id, device_name)
                        break
                
                if not device_name:
                    _LOGGER.error("Could not find device with rs90_device_id: %s", rs90_device_id)
                    return
                
                await coordinator.async_trigger_device_command(device_name, command_name)
                return
        
        _LOGGER.error("Coordinator not found for device: %s", rs90_id)
    
    async def handle_refresh_lists(call):
        """Handle the refresh_lists service call."""
        rs90_id = call.data.get("rs90_id")
        
        # Find the coordinator for this device
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(rs90_id)
        
        if not device_entry:
            _LOGGER.error("Device not found: %s", rs90_id)
            return
        
        # Find the config entry
        for entry_id in device_entry.config_entries:
            if entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN][entry_id]
                await coordinator.async_force_refresh_lists()
                _LOGGER.info("Force refresh lists requested for device: %s", rs90_id)
                return
        
        _LOGGER.error("Coordinator not found for device: %s", rs90_id)
    
    # Register services only once
    if not hass.services.has_service(DOMAIN, "trigger_macro"):
        hass.services.async_register(
            DOMAIN,
            "trigger_macro",
            handle_trigger_macro,
        )
    
    if not hass.services.has_service(DOMAIN, "trigger_device_command"):
        hass.services.async_register(
            DOMAIN,
            "trigger_device_command",
            handle_trigger_device_command,
        )
    
    if not hass.services.has_service(DOMAIN, "refresh_lists"):
        hass.services.async_register(
            DOMAIN,
            "refresh_lists",
            handle_refresh_lists,
        )


async def _async_cleanup_old_macro_info_sensors(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove old macro info sensors and device list sensor (migration v1.5.0 -> v1.6.0)."""
    from homeassistant.helpers import entity_registry as er
    
    entity_registry = er.async_get(hass)
    remote_id = entry.data["remote_id"]
    
    _LOGGER.info("=== Starting cleanup of old sensors for entry: %s ===", entry.entry_id)
    
    # Find all macro info sensors and device list sensor for this remote
    entities_to_remove = []
    all_entities = []
    
    for entity in entity_registry.entities.values():
        if entity.platform == DOMAIN and entity.config_entry_id == entry.entry_id:
            all_entities.append(f"{entity.entity_id} (unique_id: {entity.unique_id})")
            
            # Check if it's a macro info sensor (unique_id contains "macro_info_")
            # or device list sensor (unique_id ends with "_device_list")
            if entity.unique_id:
                if "macro_info_" in entity.unique_id or entity.unique_id.endswith("_device_list"):
                    entities_to_remove.append(entity.entity_id)
                    _LOGGER.info("Found old sensor to remove: %s (unique_id: %s)", entity.entity_id, entity.unique_id)
    
    _LOGGER.info("All entities for this integration: %s", all_entities)
    _LOGGER.info("Entities marked for removal: %s", entities_to_remove)
    
    # Remove all found entities
    for entity_id in entities_to_remove:
        try:
            entity_registry.async_remove(entity_id)
            _LOGGER.info("✓ Successfully removed old sensor: %s", entity_id)
        except Exception as err:
            _LOGGER.error("✗ Failed to remove sensor %s: %s", entity_id, err)
    
    if entities_to_remove:
        _LOGGER.info("=== Migration complete: Removed %d old sensors ===", len(entities_to_remove))
    else:
        _LOGGER.info("=== No old sensors found to remove ===")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Haptique RS90 Remote from a config entry."""
    _LOGGER.debug("Setting up Haptique RS90 Remote integration")
    
    # Create coordinator
    coordinator = HaptiqueRS90Coordinator(hass, entry)
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Subscribe to MQTT topics and start coordinator
    await coordinator.async_config_entry_first_refresh()
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Cleanup old sensors AFTER platforms are loaded
    await _async_cleanup_old_macro_info_sensors(hass, entry)
    
    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data["remote_id"])},
        name=entry.data.get("name", f"Haptique RS90 {entry.data['remote_id'][:8]}"),
        manufacturer="Haptique",
        model="RS90",
        sw_version="1.0",
    )
    
    # Register services
    await async_setup_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Haptique RS90 Remote integration")
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Unsubscribe from MQTT topics
        coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_shutdown()
        
        # Remove coordinator
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    _LOGGER.debug("Removing Haptique RS90 Remote integration")
