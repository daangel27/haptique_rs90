"""Config flow for Haptique RS90 Remote integration."""
from __future__ import annotations

import asyncio
import ipaddress
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_DASHBOARD_COMMANDS,
    CONF_NAME,
    CONF_REMOTE_ID,
    CONF_WAKE_AUTO,
    CONF_WAKE_HOST,
    DOMAIN,
)

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
        self._device_id: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose what to configure."""
        return self.async_show_menu(
            step_id="init", menu_options=["name", "dashboard_device", "wake"]
        )

    def _save(self, **changes: Any) -> FlowResult:
        """Store options without losing the ones set in other steps."""
        return self.async_create_entry(
            title="", data={**self._config_entry.options, **changes}
        )

    async def async_step_name(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Rename the remote."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={**self._config_entry.data, CONF_NAME: user_input[CONF_NAME]},
            )
            return self._save()

        return self.async_show_form(
            step_id="name",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=self._config_entry.data.get(
                            CONF_NAME,
                            f"RS90 {self._config_entry.data[CONF_REMOTE_ID][:8]}",
                        ),
                    ): str,
                }
            ),
        )

    def _inventory(self) -> tuple[list[dict], dict[str, list]]:
        coordinator = self.hass.data.get(DOMAIN, {}).get(self._config_entry.entry_id)
        data = (coordinator.data if coordinator else None) or {}
        return data.get("devices", []), data.get("device_commands", {})

    async def async_step_dashboard_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Pick the RS90 device whose dashboard buttons to choose."""
        devices, _ = self._inventory()
        if not devices:
            return self.async_abort(reason="no_devices")
        if user_input is not None:
            self._device_id = user_input["device"]
            return await self.async_step_dashboard_commands()

        return self.async_show_form(
            step_id="dashboard_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=device["id"], label=device["name"]
                                )
                                for device in sorted(
                                    devices, key=lambda d: str(d["name"]).lower()
                                )
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_dashboard_commands(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose the command buttons shown for one device."""
        devices, commands = self._inventory()
        device = next((d for d in devices if d["id"] == self._device_id), None)
        if device is None:
            return self.async_abort(reason="no_devices")
        available = list(
            dict.fromkeys(
                cmd["id"] for cmd in commands.get(device["name"], []) if cmd.get("id")
            )
        )
        selection = dict(self._config_entry.options.get(CONF_DASHBOARD_COMMANDS, {}))

        if user_input is not None:
            chosen = user_input.get("commands", [])
            if user_input.get("show_all") or set(chosen) == set(available):
                selection.pop(self._device_id, None)
            else:
                selection[self._device_id] = [c for c in available if c in chosen]
            return self._save(**{CONF_DASHBOARD_COMMANDS: selection})

        current = selection.get(self._device_id, available)
        return self.async_show_form(
            step_id="dashboard_commands",
            description_placeholders={"device": device["name"]},
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "show_all", default=self._device_id not in selection
                    ): bool,
                    vol.Optional(
                        "commands", default=[c for c in current if c in available]
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=available,
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )

    async def async_step_wake(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """IP address used to wake the RS90 up, and automatic wake-up."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = (user_input.get(CONF_WAKE_HOST) or "").strip()
            if host and not _valid_ipv4(host):
                errors[CONF_WAKE_HOST] = "invalid_ip"
            else:
                return self._save(
                    **{
                        CONF_WAKE_HOST: host,
                        CONF_WAKE_AUTO: bool(host and user_input.get(CONF_WAKE_AUTO)),
                    }
                )
        options = self._config_entry.options
        return self.async_show_form(
            step_id="wake",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_WAKE_HOST,
                        description={
                            "suggested_value": options.get(CONF_WAKE_HOST, "")
                        },
                    ): str,
                    vol.Optional(
                        CONF_WAKE_AUTO, default=options.get(CONF_WAKE_AUTO, False)
                    ): bool,
                }
            ),
        )


def _valid_ipv4(value: str) -> bool:
    """An IPv4 address (the RS90 has no reliable host name)."""
    try:
        return isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address)
    except ValueError:
        return False
