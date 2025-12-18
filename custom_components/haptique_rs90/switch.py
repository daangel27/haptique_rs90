"""Switch platform for Haptique RS90 Remote integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
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
    """Set up Haptique RS90 switch platform."""
    coordinator: HaptiqueRS90Coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities: dict[str, HaptiqueRS90MacroSwitch] = {}
    
    # Create switches for macros
    for macro in coordinator.data.get("macros", []):
        macro_id = macro.get("id")
        macro_name = macro.get("name")
        if macro_id and macro_name:
            entity = HaptiqueRS90MacroSwitch(coordinator, entry, macro_id, macro_name)
            entities[macro_id] = entity
    
    async_add_entities(entities.values())
    
    @callback
    def _async_update_entities() -> None:
        """Add new entities and remove obsolete ones when macros change."""
        _LOGGER.debug("=== SWITCH: Entity update triggered ===")
        entity_registry = er.async_get(hass)
        current_macro_ids = {macro.get("id") for macro in coordinator.data.get("macros", []) if macro.get("id")}
        existing_macro_ids = set(entities.keys())
        
        _LOGGER.debug("Current macro IDs from MQTT: %s", current_macro_ids)
        _LOGGER.debug("Existing macro IDs in HA: %s", existing_macro_ids)
        
        # Check for renamed macros (same ID, different name)
        for macro in coordinator.data.get("macros", []):
            macro_id = macro.get("id")
            macro_name = macro.get("name")
            if macro_id in existing_macro_ids and macro_name:
                entity = entities.get(macro_id)
                if entity and entity._macro_name != macro_name:
                    _LOGGER.info("RENAME: Macro renamed: '%s' → '%s' (id: %s)", 
                                entity._macro_name, macro_name, macro_id)
                    entity._macro_name = macro_name
                    # Update friendly name in entity registry
                    entity_reg = er.async_get(hass)
                    if entity_entry := entity_reg.async_get(entity.entity_id):
                        entity_reg.async_update_entity(
                            entity.entity_id,
                            name=f"Macro: {macro_name}"
                        )
                    # Force immediate state update
                    entity.async_write_ha_state()
                    entity.async_schedule_update_ha_state(force_refresh=True)
        
        # Find macros to add
        macros_to_add = current_macro_ids - existing_macro_ids
        new_entities = []
        
        if macros_to_add:
            _LOGGER.info("Macros to add: %s", macros_to_add)
        
        for macro in coordinator.data.get("macros", []):
            macro_id = macro.get("id")
            macro_name = macro.get("name")
            if macro_id in macros_to_add and macro_name:
                entity = HaptiqueRS90MacroSwitch(coordinator, entry, macro_id, macro_name)
                entities[macro_id] = entity
                new_entities.append(entity)
                _LOGGER.info("SUCCESS: Adding new macro switch: %s (id: %s)", macro_name, macro_id)
        
        if new_entities:
            async_add_entities(new_entities)
        
        # Find macros to remove
        macros_to_remove = existing_macro_ids - current_macro_ids
        
        if macros_to_remove:
            _LOGGER.info("Macros to remove: %s", macros_to_remove)
        
        for macro_id in macros_to_remove:
            entity = entities.pop(macro_id, None)
            if entity:
                _LOGGER.debug("Processing removal of macro: %s (unique_id: %s)", entity.name, entity.unique_id)
                # Remove from entity registry
                entity_id = entity_registry.async_get_entity_id(
                    "switch",
                    DOMAIN,
                    entity.unique_id
                )
                if entity_id:
                    entity_registry.async_remove(entity_id)
                    _LOGGER.info("SUCCESS: Removed obsolete macro switch: %s (entity_id: %s)", entity.name, entity_id)
                else:
                    _LOGGER.warning("Could not find entity_id for unique_id: %s", entity.unique_id)
            else:
                _LOGGER.warning("Could not find entity for macro_id: %s", macro_id)
    
    # Setup dynamic entity management
    entry.async_on_unload(coordinator.async_add_listener(_async_update_entities))


class HaptiqueRS90SwitchBase(CoordinatorEntity, SwitchEntity):
    """Base class for Haptique RS90 switches."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
        switch_type: str,
        switch_id: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._switch_type = switch_type
        self._switch_id = switch_id
        
        # Unique ID for the entity
        self._attr_unique_id = (
            f"{entry.data[CONF_REMOTE_ID]}_{switch_type}_{switch_id}"
        )
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data[CONF_REMOTE_ID])},
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get("status") == "online"


class HaptiqueRS90MacroSwitch(HaptiqueRS90SwitchBase):
    """Switch to control a macro on/off."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
        macro_id: str,
        macro_name: str,
    ) -> None:
        """Initialize the macro switch."""
        super().__init__(coordinator, entry, "macro", macro_id)
        
        # Store macro name - friendly_name will come from @property name
        self._macro_name = macro_name
        
        self._attr_icon = "mdi:play-circle"
        self._attr_device_class = "switch"

    @property
    def name(self) -> str:
        """Return the friendly name (updates on rename)."""
        return self._macro_name
    
    @property
    def is_on(self) -> bool:
        """Return True if the macro is currently running."""
        macro_states = self.coordinator.data.get("macro_states", {})
        current_state = macro_states.get(self._macro_name, "off")
        return current_state == "on"

    @property
    def icon(self) -> str:
        """Return dynamic icon based on state."""
        return "mdi:stop-circle" if self.is_on else "mdi:play-circle"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        macro_states = self.coordinator.data.get("macro_states", {})
        current_state = macro_states.get(self._macro_name, "off")
        return {
            "rs90_macro_id": self._switch_id,  # Stable ID for service calls
            "macro_name": self._macro_name,
            "current_state": current_state,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the macro on."""
        _LOGGER.debug("Turning on macro: %s", self._macro_name)
        await self.coordinator.async_trigger_macro(self._macro_name, "on")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the macro off."""
        _LOGGER.debug("Turning off macro: %s", self._macro_name)
        await self.coordinator.async_trigger_macro(self._macro_name, "off")
