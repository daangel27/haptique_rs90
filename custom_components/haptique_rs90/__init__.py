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
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,  # Macros as switches (on/off state visible)
]


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Haptique RS90."""
    
    async def handle_trigger_macro(call):
        """Handle the trigger_macro service call."""
        device_id = call.data.get("device_id")
        macro_name = call.data.get("macro_name")
        
        # Find the coordinator for this device
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(device_id)
        
        if not device_entry:
            _LOGGER.error("Device not found: %s", device_id)
            return
        
        # Find the config entry
        for entry_id in device_entry.config_entries:
            if entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN][entry_id]
                await coordinator.async_trigger_macro(macro_name)
                return
        
        _LOGGER.error("Coordinator not found for device: %s", device_id)
    
    async def handle_trigger_device_command(call):
        """Handle the trigger_device_command service call."""
        device_id = call.data.get("device_id")
        device_name = call.data.get("device_name")
        command_name = call.data.get("command_name")
        
        # Find the coordinator for this device
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(device_id)
        
        if not device_entry:
            _LOGGER.error("Device not found: %s", device_id)
            return
        
        # Find the config entry
        for entry_id in device_entry.config_entries:
            if entry_id in hass.data.get(DOMAIN, {}):
                coordinator = hass.data[DOMAIN][entry_id]
                await coordinator.async_trigger_device_command(device_name, command_name)
                return
        
        _LOGGER.error("Coordinator not found for device: %s", device_id)
    
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
