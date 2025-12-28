"""Device trigger support for Haptique RS90 Remote integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Trigger types
TRIGGER_BUTTON_PRESSED = "button_pressed"

# Number of buttons on RS90 hardware
MIN_BUTTON = 1
MAX_BUTTON = 24  # RS90 has 24 physical buttons

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): TRIGGER_BUTTON_PRESSED,
        vol.Required("button"): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_BUTTON, max=MAX_BUTTON)
        ),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for RS90 remote.
    
    Returns a list of all possible button press triggers (1-24).
    """
    device_registry = dr.async_get(hass)
    device = device_registry.async_get(device_id)
    
    if not device:
        return []
    
    # Check if this is an RS90 device
    if not any(identifier[0] == DOMAIN for identifier in device.identifiers):
        return []
    
    triggers = []
    
    # Generate triggers for buttons 1-24 (RS90 physical buttons)
    for button in range(MIN_BUTTON, MAX_BUTTON + 1):
        triggers.append(
            {
                CONF_PLATFORM: "device",
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: TRIGGER_BUTTON_PRESSED,
                "button": button,
            }
        )
    
    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: Any,
    trigger_info: dict[str, Any],
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    device_id = config[CONF_DEVICE_ID]
    button = config["button"]
    
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: f"{DOMAIN}_key_pressed",
            event_trigger.CONF_EVENT_DATA: {
                "device_id": device_id,
                "button": button,
            },
        }
    )
    
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )


async def async_get_trigger_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """List trigger capabilities."""
    return {
        "extra_fields": vol.Schema(
            {
                vol.Required("button"): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_BUTTON, max=MAX_BUTTON)
                )
            }
        )
    }
