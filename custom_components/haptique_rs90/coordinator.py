"""Coordinator for Haptique RS90 Remote integration."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_REMOTE_ID,
    TOPIC_BASE,
    TOPIC_STATUS,
    TOPIC_DEVICE_LIST,
    TOPIC_MACRO_LIST,
    TOPIC_BATTERY_STATUS,
    TOPIC_BATTERY_LEVEL,
    TOPIC_KEYS,
    TOPIC_TEST_STATUS,
    STATE_ONLINE,
    STATE_OFFLINE,
)

_LOGGER = logging.getLogger(__name__)


class HaptiqueRS90Coordinator(DataUpdateCoordinator):
    """Class to manage fetching Haptique RS90 data from MQTT."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        # No automatic polling - updates come only from MQTT
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # No periodic updates
        )
        
        self.entry = entry
        self.remote_id = entry.data[CONF_REMOTE_ID]
        self._subscriptions: list[callable] = []  # Global subscriptions (status, battery, etc.)
        self._macro_subscriptions: dict[str, callable] = {}  # Macro-specific subscriptions
        
        # Track subscribed devices and macros to handle add/remove
        self._subscribed_devices: set[str] = set()
        self._subscribed_macros: set[str] = set()
        
        # Data storage
        self.data: dict[str, Any] = {
            "status": STATE_OFFLINE,
            "battery_level": None,
            "last_key": None,
            "running_macro": None,
            "devices": [],
            "macros": [],
            "device_commands": {},
            "test_status": None,
            "macro_states": {},  # Store macro states (on/off) from MQTT only
        }
        
        _LOGGER.info("Coordinator initialized - updates via MQTT only")

    @property
    def base_topic(self) -> str:
        """Return base MQTT topic for this remote."""
        return f"{TOPIC_BASE}/{self.remote_id}"

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh and subscribe to MQTT topics."""
        # Subscribe to MQTT topics
        await self._subscribe_topics()
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data - returns current data as updates come from MQTT."""
        # No polling needed - all updates come via MQTT callbacks
        # This method is called during initial setup and returns current data
        return self.data

    async def _subscribe_topics(self) -> None:
        """Subscribe to MQTT topics."""
        _LOGGER.debug("Subscribing to MQTT topics for remote %s", self.remote_id)
        
        # Subscribe to status topic
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_STATUS}",
            self._handle_status
        )
        
        # Subscribe to device list
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_DEVICE_LIST}",
            self._handle_device_list
        )
        
        # Subscribe to macro list
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_MACRO_LIST}",
            self._handle_macro_list
        )
        
        # Subscribe to battery level (receives value after publishing to battery/status)
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_BATTERY_LEVEL}",
            self._handle_battery
        )
        _LOGGER.info("Subscribed to battery_level topic")
        
        # Subscribe to key events
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_KEYS}",
            self._handle_keys
        )
        
        # Subscribe to test status (for running macro detection)
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_TEST_STATUS}",
            self._handle_test_status
        )
        
        # Request initial battery level by publishing to battery/status
        # This triggers the remote to publish the value on battery_level
        battery_trigger_topic = f"{self.base_topic}/{TOPIC_BATTERY_STATUS}"
        _LOGGER.info("Publishing to %s to trigger battery level update", battery_trigger_topic)
        try:
            _LOGGER.debug("📤 MQTT PUBLISH: topic='%s', payload='', qos=0, retain=False", battery_trigger_topic)
            await mqtt.async_publish(
                self.hass,
                battery_trigger_topic,
                "",  # Empty payload to trigger update
                qos=0,  # QoS 0 for monitoring requests (Haptique best practice)
                retain=False
            )
            _LOGGER.info("✓ Battery level trigger published successfully")
        except Exception as err:
            _LOGGER.error("✗ Failed to publish battery trigger: %s", err)

    async def _subscribe(self, topic: str, callback_func: callable, qos: int = 0) -> callable:
        """Subscribe to an MQTT topic.
        
        Args:
            topic: MQTT topic to subscribe to
            callback_func: Function to call when message received
            qos: Quality of Service (0 for monitoring, 1 for control commands)
                 Default is 0 as per Haptique best practices for monitoring
        
        Returns:
            Unsubscribe function
        """
        @callback
        def message_received(msg):
            """Handle new MQTT message."""
            # msg.payload is already a string (decoded by Home Assistant)
            payload_str = str(msg.payload)[:100] if msg.payload else ""
            _LOGGER.debug("📥 MQTT received on '%s': payload='%s' (len=%d)", 
                         topic, payload_str, len(msg.payload) if msg.payload else 0)
            callback_func(msg.payload)
        
        _LOGGER.debug("📡 MQTT SUBSCRIBE: topic='%s', qos=%d", topic, qos)
        _LOGGER.info("Attempting to subscribe to MQTT topic: %s (QoS %d)", topic, qos)
        try:
            unsubscribe = await mqtt.async_subscribe(
                self.hass, topic, message_received, qos=qos
            )
            self._subscriptions.append(unsubscribe)
            _LOGGER.info("✓ Successfully subscribed to topic: %s (QoS %d)", topic, qos)
            return unsubscribe
        except Exception as err:
            _LOGGER.error("✗ Failed to subscribe to topic %s: %s", topic, err)
            return None

    @callback
    def _handle_status(self, payload: str) -> None:
        """Handle status message."""
        status = payload.strip()
        old_status = self.data.get("status")
        
        if status != old_status:
            _LOGGER.info("Status changed: %s → %s", old_status, status)
            self.data["status"] = status
            self.async_set_updated_data(self.data)
        else:
            _LOGGER.debug("Status unchanged: %s", status)

    @callback
    def _handle_device_list(self, payload: str) -> None:
        """Handle device list message and manage subscriptions."""
        try:
            devices = json.loads(payload)
            _LOGGER.debug("Received device list: %s", devices)
            
            # Normalize ID field (handle both "id" and "Id")
            normalized_devices = []
            current_device_names = set()
            
            for device in devices:
                normalized_device = {
                    "id": device.get("id") or device.get("Id"),
                    "name": device.get("name")
                }
                normalized_devices.append(normalized_device)
                device_name = normalized_device.get("name")
                if device_name:
                    current_device_names.add(device_name)
            
            self.data["devices"] = normalized_devices
            _LOGGER.debug("Normalized devices: %s", normalized_devices)
            
            # Detect new devices (not yet subscribed)
            new_devices = current_device_names - self._subscribed_devices
            
            # Detect removed devices (subscribed but not in current list)
            removed_devices = self._subscribed_devices - current_device_names
            
            # Subscribe to new devices
            for device_name in new_devices:
                _LOGGER.info("🆕 New device detected: %s - subscribing to details", device_name)
                asyncio.create_task(
                    self._subscribe_device_details(device_name)
                )
                self._subscribed_devices.add(device_name)
            
            # Clean up removed devices
            for device_name in removed_devices:
                _LOGGER.info("🗑️ Device removed: %s - cleaning up", device_name)
                self._subscribed_devices.discard(device_name)
                # Remove commands from storage
                if device_name in self.data["device_commands"]:
                    del self.data["device_commands"][device_name]
                    _LOGGER.debug("Removed commands for deleted device: %s", device_name)
            
            self.async_set_updated_data(self.data)
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse device list: %s", payload)

    @callback
    def _handle_macro_list(self, payload: str) -> None:
        """Handle macro list message and manage subscriptions."""
        try:
            macros = json.loads(payload)
            _LOGGER.debug("Received macro list: %s", macros)
            
            # Normalize ID field (handle both "id" and "Id")
            normalized_macros = []
            current_macro_names = set()
            
            for macro in macros:
                normalized_macro = {
                    "id": macro.get("id") or macro.get("Id"),
                    "name": macro.get("name")
                }
                normalized_macros.append(normalized_macro)
                macro_name = normalized_macro.get("name")
                if macro_name:
                    current_macro_names.add(macro_name)
            
            self.data["macros"] = normalized_macros
            _LOGGER.debug("Normalized macros: %s", normalized_macros)
            
            # Detect new macros (not yet subscribed)
            new_macros = current_macro_names - self._subscribed_macros
            
            # Detect removed macros (subscribed but not in current list)
            removed_macros = self._subscribed_macros - current_macro_names
            
            _LOGGER.debug("Macro cleanup check - Current: %s, Subscribed: %s, To remove: %s", 
                         current_macro_names, self._subscribed_macros, removed_macros)
            
            # Subscribe to new macros
            for macro_name in new_macros:
                _LOGGER.info("🆕 New macro detected: %s - subscribing to trigger", macro_name)
                asyncio.create_task(
                    self._subscribe_macro_trigger(macro_name)
                )
                # Note: macro_name will be added to _subscribed_macros inside _subscribe_macro_trigger()
            
            # Clean up removed macros
            for macro_name in removed_macros:
                _LOGGER.info("🗑️ Macro removed: %s - cleaning up", macro_name)
                self._subscribed_macros.discard(macro_name)
                
                # Unsubscribe from this macro's trigger topic
                trigger_topic = f"{self.base_topic}/macro/{macro_name}/trigger"
                _LOGGER.debug("Checking macro_subscriptions dict, keys: %s", list(self._macro_subscriptions.keys()))
                if macro_name in self._macro_subscriptions:
                    _LOGGER.debug("📡 MQTT UNSUBSCRIBE: topic='%s'", trigger_topic)
                    unsubscribe_func = self._macro_subscriptions.pop(macro_name)
                    unsubscribe_func()
                    _LOGGER.info("✓ Unsubscribed from macro trigger: %s", macro_name)
                else:
                    _LOGGER.warning("⚠️ Macro %s not found in subscriptions dict!", macro_name)
                
                # Remove state from memory
                if macro_name in self.data["macro_states"]:
                    del self.data["macro_states"][macro_name]
                    _LOGGER.debug("Removed state for deleted macro: %s", macro_name)
            
            self.async_set_updated_data(self.data)
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse macro list: %s", payload)

    @callback
    def _handle_battery(self, payload: str) -> None:
        """Handle battery level message from battery_level topic."""
        try:
            payload = payload.strip()
            _LOGGER.debug("Raw battery_level payload: '%s'", payload)
            
            battery_level = None
            
            # Topic battery_level should contain direct value (0-100)
            # Format 1: Just the number "85"
            if payload.isdigit():
                battery_level = int(payload)
            # Format 2: With percent "85%"
            elif "%" in payload:
                battery_str = payload.replace("%", "").strip()
                if battery_str.isdigit():
                    battery_level = int(battery_str)
            # Format 3: Any text with a number (fallback)
            else:
                import re
                numbers = re.findall(r'\d+', payload)
                if numbers:
                    battery_level = int(numbers[0])
            
            if battery_level is not None:
                # Clamp to 0-100
                battery_level = max(0, min(100, battery_level))
                _LOGGER.info("Battery level updated: %d%%", battery_level)
                self.data["battery_level"] = battery_level
                self.async_set_updated_data(self.data)
            else:
                _LOGGER.warning("Could not parse battery level from: %s", payload)
        except (ValueError, TypeError) as err:
            _LOGGER.error("Failed to parse battery level: %s - %s", payload, err)

    @callback
    def _handle_keys(self, payload: str) -> None:
        """Handle key press events."""
        try:
            # Payload format: "button:#"
            if "button:" in payload:
                button_num = payload.split("button:")[1].strip()
                _LOGGER.debug("Key pressed: button %s", button_num)
                self.data["last_key"] = button_num
                self.async_set_updated_data(self.data)
            else:
                _LOGGER.warning("Unexpected key payload format: %s", payload)
        except (IndexError, AttributeError) as err:
            _LOGGER.error("Failed to parse key event: %s - %s", payload, err)

    @callback
    def _handle_test_status(self, payload: str) -> None:
        """Handle test status message (running macro info)."""
        _LOGGER.debug("Test status: %s", payload)
        self.data["test_status"] = payload
        
        # Try to extract running macro/device info
        # Format: "Pioneer - VSX/SC Series - Off 200"
        if payload and payload != "":
            self.data["running_macro"] = payload
        else:
            self.data["running_macro"] = None
            
        self.async_set_updated_data(self.data)

    async def _subscribe_device_details(self, device_name: str) -> None:
        """Subscribe to device commands topic (retained message)."""
        # Based on actual MQTT data, commands are published on /commands topic (retained)
        topic_commands = f"{self.base_topic}/device/{device_name}/commands"
        
        @callback
        def handle_device_commands(payload: str) -> None:
            """Handle device commands message."""
            _LOGGER.debug("Received payload on /commands for device '%s': %s", device_name, payload[:200] if payload else "None")
            
            # Ignore empty payloads
            if not payload or payload.strip() == "":
                _LOGGER.debug("Received empty payload for device '%s' - ignoring", device_name)
                return
            
            try:
                commands = json.loads(payload)
                _LOGGER.info("✓ Received %d commands for device '%s'", len(commands), device_name)
                
                # Normalize ID field (handle both "id", "Id", "ID")
                normalized_commands = []
                for command in commands:
                    cmd_id = command.get("id") or command.get("Id") or command.get("ID")
                    normalized_command = {
                        "id": cmd_id,
                        "name": command.get("name")
                    }
                    normalized_commands.append(normalized_command)
                    _LOGGER.debug("Normalized command: id=%s, name=%s", normalized_command.get("id"), normalized_command.get("name"))
                
                self.data["device_commands"][device_name] = normalized_commands
                _LOGGER.info("✓ Stored %d normalized commands for '%s'", len(normalized_commands), device_name)
                _LOGGER.debug("Current device_commands keys: %s", list(self.data["device_commands"].keys()))
                self.async_set_updated_data(self.data)
            except json.JSONDecodeError as err:
                _LOGGER.error("Failed to parse device commands for %s: %s - Error: %s", device_name, payload, err)
        
        # Subscribe to /commands topic (retained message will be delivered immediately)
        await self._subscribe(topic_commands, handle_device_commands)
        _LOGGER.info("✓ Subscribed to retained topic: %s", topic_commands)

    async def _subscribe_macro_trigger(self, macro_name: str) -> None:
        """Subscribe to macro trigger topic for state tracking."""
        topic = f"{self.base_topic}/macro/{macro_name}/trigger"
        
        @callback
        def handle_macro_trigger(payload: str) -> None:
            """Handle macro trigger state."""
            state = payload.strip().lower()
            _LOGGER.debug("Macro %s trigger state received: %s", macro_name, state)
            
            # Store the macro state in memory only
            if state in ["on", "off"]:
                self.data["macro_states"][macro_name] = state
                _LOGGER.info("✓ Macro '%s' state updated to: %s", macro_name, state)
                self.async_set_updated_data(self.data)
            else:
                _LOGGER.warning("Invalid macro state '%s' for macro '%s', expected 'on' or 'off'", state, macro_name)
        
        unsubscribe = await self._subscribe(topic, handle_macro_trigger, qos=1)  # QoS 1 for control state
        
        # Only add to tracking if subscription succeeded
        if unsubscribe:
            self._macro_subscriptions[macro_name] = unsubscribe
            self._subscribed_macros.add(macro_name)  # Add AFTER successful subscription
            _LOGGER.info("✓ Subscribed to macro trigger: %s", topic)
        else:
            _LOGGER.error("Failed to subscribe to macro trigger: %s", topic)

    async def async_trigger_macro(self, macro_name: str, action: str = "on") -> None:
        """Trigger a macro with ON or OFF action."""
        topic = f"{self.base_topic}/macro/{macro_name}/trigger"
        _LOGGER.debug("Triggering macro: %s with action: %s", macro_name, action)
        
        # Publish without retain - RS90 manages its own state
        _LOGGER.debug("📤 MQTT PUBLISH (MACRO): topic='%s', payload='%s', qos=1, retain=False", topic, action)
        await mqtt.async_publish(self.hass, topic, action, qos=1, retain=False)
        
        # Update local state immediately (will be confirmed by MQTT callback)
        self.data["macro_states"][macro_name] = action
        self.async_set_updated_data(self.data)

    async def async_trigger_device_command(self, device_name: str, command_name: str) -> None:
        """Trigger a device command."""
        topic = f"{self.base_topic}/device/{device_name}/trigger"
        _LOGGER.debug("Triggering command %s for device %s", command_name, device_name)
        _LOGGER.debug("📤 MQTT PUBLISH (DEVICE): topic='%s', payload='%s', qos=1, retain=False", topic, command_name)
        await mqtt.async_publish(self.hass, topic, command_name, qos=1, retain=False)

    async def async_shutdown(self) -> None:
        """Unsubscribe from all MQTT topics."""
        _LOGGER.debug("Shutting down coordinator for remote %s", self.remote_id)
        
        # Unsubscribe from all global topics
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()
        
        # Unsubscribe from all macro-specific topics
        for macro_name, unsubscribe in self._macro_subscriptions.items():
            unsubscribe()
            _LOGGER.debug("Unsubscribed from macro: %s", macro_name)
        self._macro_subscriptions.clear()

    async def async_force_refresh_lists(self) -> None:
        """Force refresh of device and macro lists by re-requesting from RS90.
        
        Note: Since device/list and macro/list are retained topics, we cannot
        force the RS90 to republish. This method logs the current state for diagnosis.
        If lists are not updating, the RS90 may need to be restarted.
        """
        _LOGGER.warning("Force refresh lists requested - checking current state")
        _LOGGER.info("Current devices: %s", [d.get("name") for d in self.data.get("devices", [])])
        _LOGGER.info("Current macros: %s", [m.get("name") for m in self.data.get("macros", [])])
        _LOGGER.info("Subscribed devices: %s", self._subscribed_devices)
        _LOGGER.info("Subscribed macros: %s", self._subscribed_macros)
        
        # Note: We cannot force RS90 to republish retained messages
        # The RS90 should automatically publish updated lists when macros/devices change
        # If not receiving updates, try restarting the RS90 hardware
        _LOGGER.warning(
            "⚠️ If lists are not updating after changes in Haptique Config app, "
            "the RS90 may need to be restarted to publish updated lists to MQTT"
        )

    def get_diagnostics(self) -> dict:
        """Get diagnostic information."""
        # Build detailed device_commands info
        device_commands_detail = {}
        for device, commands in self.data.get("device_commands", {}).items():
            device_commands_detail[device] = {
                "count": len(commands),
                "command_ids": [cmd.get("id") for cmd in commands if cmd.get("id")],
                "commands_full": commands[:5]  # Show first 5 commands as sample
            }
        
        return {
            "remote_id": self.remote_id,
            "status": self.data.get("status"),
            "devices_count": len(self.data.get("devices", [])),
            "devices": self.data.get("devices", []),
            "macros_count": len(self.data.get("macros", [])),
            "macros": self.data.get("macros", []),
            "device_commands": device_commands_detail,
            "device_commands_keys": list(self.data.get("device_commands", {}).keys()),
            "subscriptions_count": len(self._subscriptions),
            "subscribed_devices": list(self._subscribed_devices),
        }
