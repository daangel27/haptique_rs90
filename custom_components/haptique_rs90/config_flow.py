"""Config flow for Haptique RS90 Remote integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_REMOTE_ID, CONF_NAME

_LOGGER = logging.getLogger(__name__)


class HaptiqueRS90ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Haptique RS90 Remote."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        # Check if MQTT is configured
        if not await mqtt.async_wait_for_mqtt_client(self.hass):
            return self.async_abort(reason="mqtt_not_configured")

        if user_input is not None:
            # Use the discovered remote_id or default
            remote_id = self.context.get("remote_id", "")
            
            if not remote_id:
                errors["base"] = "no_remote_found"
            else:
                # Check if already configured
                await self.async_set_unique_id(remote_id)
                self._abort_if_unique_id_configured()
                
                # Create entry
                device_name = user_input.get(CONF_NAME, f"RS90 {remote_id[:8]}")
                return self.async_create_entry(
                    title=device_name,
                    data={
                        CONF_REMOTE_ID: remote_id,
                        CONF_NAME: device_name,
                    },
                )

        # Try to discover remote automatically
        discovered_remote = await self._discover_remote()
        
        if discovered_remote:
            self.context["remote_id"] = discovered_remote
            remote_display = f"{discovered_remote[:8]}..."
        else:
            remote_display = "Non trouvé"
            errors["base"] = "no_remote_found"

        # Show configuration form
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=f"RS90 Salon"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "remote_id": remote_display,
            },
        )

    async def _discover_remote(self) -> str | None:
        """Try to discover a Haptique RS90 remote on MQTT."""
        _LOGGER.info("Attempting to discover Haptique RS90 remote...")
        
        discovered_id = None
        
        @callback
        def remote_discovered(msg):
            """Handle discovered remote."""
            nonlocal discovered_id
            # Extract remote ID from topic: Haptique/{RemoteID}/status
            topic_parts = msg.topic.split("/")
            if len(topic_parts) >= 2 and topic_parts[0] == "Haptique":
                discovered_id = topic_parts[1]
                _LOGGER.info("Discovered Haptique RS90 with ID: %s", discovered_id)
        
        # Subscribe to discovery topic
        unsubscribe = await mqtt.async_subscribe(
            self.hass, "Haptique/+/status", remote_discovered, qos=1
        )
        
        # Wait a bit for discovery
        await asyncio.sleep(2)
        
        # Unsubscribe
        unsubscribe()
        
        return discovered_id

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HaptiqueRS90OptionsFlow:
        """Get the options flow for this handler."""
        return HaptiqueRS90OptionsFlow(config_entry)


class HaptiqueRS90OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Haptique RS90 Remote."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry with new name
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={
                    **self._config_entry.data,
                    CONF_NAME: user_input[CONF_NAME],
                },
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=self._config_entry.data.get(
                            CONF_NAME,
                            f"RS90 {self._config_entry.data[CONF_REMOTE_ID][:8]}"
                        ),
                    ): str,
                }
            ),
        )
