"""Coordinator for Haptique RS90 Remote integration."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_REMOTE_ID,
    DOMAIN,
    STATE_OFFLINE,
    STATE_ONLINE,
    TOPIC_BASE,
    TOPIC_BATTERY_LEVEL,
    TOPIC_BATTERY_STATUS,
    TOPIC_DEVICE_LIST,
    TOPIC_KEYS,
    TOPIC_LED_LIGHT,
    TOPIC_MACRO_LIST,
    TOPIC_STATUS,
    TOPIC_TEST_STATUS,
)
from .targets import TargetManager, parse_inventory

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
        self.device_id = None  # Will be set after device registration
        self._subscriptions: list[
            callable
        ] = []  # Global subscriptions (status, battery, etc.)
        self._tasks: set[asyncio.Task] = set()
        self._closed = False
        self._device_subscriptions: dict[str, callable] = {}
        self._device_task: asyncio.Task | None = None
        self._devices_dirty = False

        # Track subscribed devices and macros to handle add/remove
        self._subscribed_devices: set[str] = set()
        self._subscribed_macros: set[str] = set()

        # Battery refresh timer
        self._battery_refresh_timer: callable | None = None
        self._battery_refresh_interval = 1800  # 30 minutes in seconds
        self._last_battery_refresh: float = 0  # Timestamp of last battery refresh
        self._battery_refresh_min_interval = 300  # 5 minutes minimum between refreshes

        # LED light auto-off timer
        self._led_light_timer: callable | None = None

        # Data storage
        self.data: dict[str, Any] = {
            "status": STATE_OFFLINE,
            "battery_level": None,
            "last_key": None,
            "running_macro": None,
            "devices": [],
            "macros": [],
            "sequences": [],
            "sequence_states": {},
            "device_commands": {},
            "test_status": None,
            "macro_states": {},  # Store macro states (on/off) from MQTT only
            "led_light_state": "off",  # RGB ring light state
            "led_light_duration": 5,  # Default duration in seconds
        }

        self.targets = TargetManager(self)
        _LOGGER.info("Coordinator initialized - updates via MQTT only")

    def _create_task(self, coroutine) -> asyncio.Task:
        """Own setup/reconnection work so unload cannot leak callbacks."""
        task = self.hass.async_create_task(coroutine)
        self._tasks.add(task)

        def done(completed):
            self._tasks.discard(completed)
            if not completed.cancelled() and (error := completed.exception()):
                _LOGGER.error("MQTT setup/update failed: %s", error)

        task.add_done_callback(done)
        return task

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
        await self._subscribe(f"{self.base_topic}/{TOPIC_STATUS}", self._handle_status)

        # Subscribe to device list
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_DEVICE_LIST}", self._handle_device_list
        )

        # Subscribe to macro list
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_MACRO_LIST}", self._handle_macro_list
        )

        await self._subscribe(
            f"{self.base_topic}/sequence/list", self._handle_sequence_list
        )

        # Subscribe to battery level (receives value after publishing to battery/status)
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_BATTERY_LEVEL}", self._handle_battery
        )
        _LOGGER.info("Subscribed to battery_level topic")

        # Subscribe to key events
        await self._subscribe(f"{self.base_topic}/{TOPIC_KEYS}", self._handle_keys)

        # Subscribe to test status (for running macro detection)
        await self._subscribe(
            f"{self.base_topic}/{TOPIC_TEST_STATUS}", self._handle_test_status
        )

        # Request initial battery level by publishing to battery/status
        # This triggers the remote to publish the value on battery_level
        battery_trigger_topic = f"{self.base_topic}/{TOPIC_BATTERY_STATUS}"
        _LOGGER.info(
            "Publishing to %s to trigger battery level update", battery_trigger_topic
        )
        try:
            _LOGGER.debug(
                "MQTT PUBLISH: topic='%s', payload='', qos=0, retain=False",
                battery_trigger_topic,
            )
            await mqtt.async_publish(
                self.hass,
                battery_trigger_topic,
                "",  # Empty payload to trigger update
                qos=0,  # QoS 0 for monitoring requests (Haptique best practice)
                retain=False,
            )
            _LOGGER.info("SUCCESS: Battery level trigger published successfully")
        except Exception as err:
            _LOGGER.error("✗ Failed to publish battery trigger: %s", err)

        # Start periodic battery refresh timer
        self._start_battery_refresh_timer()

    async def _subscribe(
        self,
        topic: str,
        callback_func: callable,
        qos: int = 0,
        add_to_global: bool = True,
    ) -> callable:
        """Subscribe to an MQTT topic.

        Args:
            topic: MQTT topic to subscribe to
            callback_func: Function to call when message received
            qos: Quality of Service (0 for monitoring, 1 for control commands)
                 Default is 0 as per Haptique best practices for monitoring
            add_to_global: If True, add to global subscriptions list for shutdown
                          Set to False for subscriptions managed separately (e.g., macros)

        Returns:
            Unsubscribe function
        """

        @callback
        def message_received(msg):
            """Handle new MQTT message."""
            # msg.payload is already a string (decoded by Home Assistant)
            payload_str = str(msg.payload)[:100] if msg.payload else ""
            _LOGGER.debug(
                "MQTT received on '%s': payload='%s' (len=%d)",
                topic,
                payload_str,
                len(msg.payload) if msg.payload else 0,
            )
            if not self._closed:
                callback_func(msg.payload)

        _LOGGER.debug("MQTT SUBSCRIBE: topic='%s', qos=%d", topic, qos)
        _LOGGER.info("Attempting to subscribe to MQTT topic: %s (QoS %d)", topic, qos)
        try:
            unsubscribe = await mqtt.async_subscribe(
                self.hass, topic, message_received, qos=qos
            )
            if self._closed:
                unsubscribe()
                return None
            # Only add to global list if requested (avoid double-tracking)
            if add_to_global:
                self._subscriptions.append(unsubscribe)
            _LOGGER.info(
                "SUCCESS: Successfully subscribed to topic: %s (QoS %d)", topic, qos
            )
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

            # Request battery update when RS90 comes back online
            # This optimizes battery refresh for sleep/wake cycles
            if status == STATE_ONLINE and old_status == STATE_OFFLINE:
                _LOGGER.info("RS90 reconnected - requesting battery update")
                self._create_task(self._request_battery_update_now())
                self._create_task(self.targets.async_query_all())
        else:
            _LOGGER.debug("Status unchanged: %s", status)

    async def _request_battery_update_now(self) -> None:
        """Request battery update immediately (called on reconnection).

        Throttled to maximum once per 5 minutes to avoid spam if RS90
        has unstable connection (frequent disconnect/reconnect cycles).
        """
        import time

        current_time = time.time()
        time_since_last_refresh = current_time - self._last_battery_refresh

        # Throttle: minimum 5 minutes between battery refreshes
        if time_since_last_refresh < self._battery_refresh_min_interval:
            _LOGGER.debug(
                "Battery refresh throttled (last refresh %.0f seconds ago, minimum %d seconds)",
                time_since_last_refresh,
                self._battery_refresh_min_interval,
            )
            return

        battery_trigger_topic = f"{self.base_topic}/{TOPIC_BATTERY_STATUS}"
        _LOGGER.debug(
            "Battery refresh on reconnection - publishing to %s", battery_trigger_topic
        )
        try:
            await mqtt.async_publish(
                self.hass, battery_trigger_topic, "", qos=0, retain=False
            )
            self._last_battery_refresh = current_time
            _LOGGER.debug("Battery refresh request sent on reconnection")
        except Exception as err:
            _LOGGER.error("Failed to send battery refresh on reconnection: %s", err)
        except Exception as err:
            _LOGGER.error("Failed to send battery refresh on reconnection: %s", err)

    @callback
    def _handle_device_list(self, payload: str) -> None:
        """Keep the last usable snapshot and reconcile device subscriptions."""
        try:
            self.data["devices"] = parse_inventory(payload)
        except (ValueError, TypeError) as err:
            _LOGGER.warning("Invalid device inventory: %s", err)
            return
        self.async_set_updated_data(self.data)
        self._devices_dirty = True
        if self._device_task is None or self._device_task.done():
            self._device_task = self._create_task(self._sync_devices())

    async def _sync_devices(self) -> None:
        while self._devices_dirty and not self._closed:
            self._devices_dirty = False
            names = {record["name"] for record in self.data["devices"]}
            for name in set(self._device_subscriptions) - names:
                self._device_subscriptions.pop(name)()
                self.data["device_commands"].pop(name, None)
            for name in names - self._device_subscriptions.keys():
                unsubscribe = await self._subscribe_device_details(name)
                if unsubscribe:
                    self._device_subscriptions[name] = unsubscribe
            self._subscribed_devices = set(self._device_subscriptions)

    @callback
    def _handle_macro_list(self, payload: str) -> None:
        self._handle_target_list("macro", payload)

    @callback
    def _handle_sequence_list(self, payload: str) -> None:
        self._handle_target_list("sequence", payload)

    def _handle_target_list(self, kind: str, payload: str) -> None:
        try:
            records = parse_inventory(payload)
        except (ValueError, TypeError) as err:
            _LOGGER.warning("Invalid %s inventory: %s", kind, err)
            return
        self.targets.update_inventory(kind, records)

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

                numbers = re.findall(r"\d+", payload)
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

                # Fire Home Assistant event for EVERY key press (including duplicates)
                # This allows automations to trigger on repeated button presses
                self.hass.bus.async_fire(
                    f"{DOMAIN}_key_pressed",
                    {
                        "remote_id": self.remote_id,
                        "device_id": self.device_id,  # HA device ID for device triggers
                        "button": int(button_num),
                        "timestamp": time.time(),  # Ensures uniqueness
                    },
                )
                _LOGGER.debug(
                    "Fired event: %s_key_pressed with button %s", DOMAIN, button_num
                )

                # Update sensor state (for backward compatibility)
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

    async def _subscribe_device_details(self, device_name: str):
        """Listen before requesting commands, including non-retained replies."""
        topic = f"{self.base_topic}/device/{device_name}/commands"

        @callback
        def handle_commands(payload: str) -> None:
            if device_name not in {item["name"] for item in self.data["devices"]}:
                return
            try:
                commands = [] if not payload.strip() else json.loads(payload)
                if not isinstance(commands, list) or any(
                    not isinstance(command, dict) for command in commands
                ):
                    raise ValueError("Commands must be an array of objects")
                self.data["device_commands"][device_name] = [
                    {
                        "id": command.get("id")
                        or command.get("Id")
                        or command.get("ID"),
                        "name": command.get("name"),
                    }
                    for command in commands
                ]
            except (ValueError, TypeError) as err:
                _LOGGER.warning("Invalid commands for %s: %s", device_name, err)
                return
            self.async_set_updated_data(self.data)

        unsubscribe = await self._subscribe(topic, handle_commands, add_to_global=False)
        if unsubscribe:
            try:
                await mqtt.async_publish(
                    self.hass,
                    f"{self.base_topic}/device/{device_name}/detail",
                    "",
                    qos=0,
                    retain=False,
                )
            except BaseException:
                unsubscribe()
                raise
        return unsubscribe

    async def async_trigger_target(
        self, kind: str, target_id: str, action: str
    ) -> None:
        """Send a non-retained ID command; feedback alone establishes state."""
        target = self.targets.require(kind, target_id)
        if action not in ("on", "off"):
            raise HomeAssistantError("Action must be on or off")
        if action == "off" and target.get("supportsOff") is False:
            raise HomeAssistantError("This macro does not support off")
        await mqtt.async_publish(
            self.hass,
            f"{self.base_topic}/{kind}/{target_id}/trigger",
            action,
            qos=1,
            retain=False,
        )

    async def async_trigger_macro(self, target_id: str, action: str = "on") -> None:
        """Keep the existing action compatible with migrated sequences."""
        kind = "macro" if self.targets.target("macro", target_id) else "sequence"
        await self.async_trigger_target(kind, target_id, action)

    async def async_query_status(self, kind: str, target_id: str) -> None:
        self.targets.require(kind, target_id)
        await self.targets.async_reconcile()
        await self.targets.async_query(kind, target_id)

    async def async_trigger_device_command(
        self, device_name: str, command_name: str
    ) -> None:
        """Trigger a device command."""
        topic = f"{self.base_topic}/device/{device_name}/trigger"
        _LOGGER.debug("Triggering command %s for device %s", command_name, device_name)
        _LOGGER.debug(
            "MQTT PUBLISH (DEVICE): topic='%s', payload='%s', qos=1, retain=False",
            topic,
            command_name,
        )
        await mqtt.async_publish(self.hass, topic, command_name, qos=1, retain=False)

    async def async_control_led_light(self, state: str, duration: int = 5) -> None:
        """Control RGB ring light animation.

        Args:
            state: "on" or "off"
            duration: Duration in seconds (1-10) when turning on

        Note:
            - Uses retain=False to prevent replay on RS90 reconnect
            - No MQTT OFF command sent (RS90 handles auto-off internally)
            - Local timer tracks state for Home Assistant UI only
        """
        topic = f"{self.base_topic}/{TOPIC_LED_LIGHT}"

        # Cancel existing timer if any
        if self._led_light_timer:
            self._led_light_timer()
            self._led_light_timer = None

        if state == "on":
            # Clamp duration between 1 and 10 seconds
            duration = max(1, min(10, duration))
            payload = str(duration)
            _LOGGER.debug("Turning on LED light for %d seconds", duration)

            # Send MQTT command with retain=False to avoid replay on reconnect
            _LOGGER.debug(
                "MQTT PUBLISH (LED): topic='%s', payload='%s', qos=1, retain=False",
                topic,
                payload,
            )
            await mqtt.async_publish(self.hass, topic, payload, qos=1, retain=False)

            # Schedule local state update (no MQTT OFF command needed)
            async def _auto_turn_off(_now=None):
                """Automatically update local state after duration (RS90 handles actual off)."""
                _LOGGER.debug("LED light duration expired, updating local state to OFF")
                self.data["led_light_state"] = "off"
                self.data["led_light_duration"] = 0
                self.async_set_updated_data(self.data)
                self._led_light_timer = None

            from homeassistant.helpers.event import async_call_later

            self._led_light_timer = async_call_later(
                self.hass, duration, _auto_turn_off
            )
        else:
            # Manual OFF: cancel timer, update local state only (no MQTT command)
            _LOGGER.debug("Turning off LED light (local state only, no MQTT)")

        # Update local state
        self.data["led_light_state"] = state
        self.data["led_light_duration"] = duration if state == "on" else 0
        self.async_set_updated_data(self.data)

    async def async_shutdown(self) -> None:
        """Unsubscribe from all MQTT topics and cancel timers."""
        if self._closed:
            return
        self._closed = True
        await self.targets.async_close()
        for task in list(self._tasks):
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        _LOGGER.debug("Shutting down coordinator for remote %s", self.remote_id)

        # Cancel battery refresh timer
        if self._battery_refresh_timer:
            self._battery_refresh_timer()
            self._battery_refresh_timer = None
            _LOGGER.debug("Cancelled battery refresh timer")

        # Cancel LED light timer
        if self._led_light_timer:
            self._led_light_timer()
            self._led_light_timer = None
            _LOGGER.debug("Cancelled LED light timer")

        # Unsubscribe from all global topics
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()

        for unsubscribe in self._device_subscriptions.values():
            unsubscribe()
        self._device_subscriptions.clear()
        if parent_shutdown := getattr(super(), "async_shutdown", None):
            await parent_shutdown()

    def _start_battery_refresh_timer(self) -> None:
        """Start periodic battery level refresh timer.

        The RS90 doesn't automatically push battery updates, so we need to
        periodically request them by publishing to battery/status topic.
        """

        async def _refresh_battery(_now=None):
            """Request battery level update."""
            battery_trigger_topic = f"{self.base_topic}/{TOPIC_BATTERY_STATUS}"
            _LOGGER.debug(
                "Periodic battery refresh - publishing to %s", battery_trigger_topic
            )
            try:
                await mqtt.async_publish(
                    self.hass, battery_trigger_topic, "", qos=0, retain=False
                )
                _LOGGER.debug("SUCCESS: Battery refresh request sent")
            except Exception as err:
                _LOGGER.error("✗ Failed to send battery refresh request: %s", err)

        from datetime import timedelta

        from homeassistant.helpers.event import async_track_time_interval

        # Schedule periodic refresh - async_track_time_interval handles thread safety
        self._battery_refresh_timer = async_track_time_interval(
            self.hass,
            _refresh_battery,  # Pass async function directly
            timedelta(seconds=self._battery_refresh_interval),
        )
        _LOGGER.info(
            "Started battery refresh timer (interval: %d seconds)",
            self._battery_refresh_interval,
        )

    async def async_force_refresh_lists(self) -> None:
        """Request a new remote snapshot, battery and confirmed target states."""
        await mqtt.async_publish(
            self.hass, f"{self.base_topic}/discovery/refresh", "", qos=0, retain=False
        )
        await mqtt.async_publish(
            self.hass,
            f"{self.base_topic}/{TOPIC_BATTERY_STATUS}",
            "",
            qos=0,
            retain=False,
        )
        await self.targets.async_query_all()
        # Older firmware ignores discovery/refresh; keep its detail requests.
        for device in self.data["devices"]:
            await mqtt.async_publish(
                self.hass,
                f"{self.base_topic}/device/{device['name']}/detail",
                "",
                qos=0,
                retain=False,
            )

    def get_diagnostics(self) -> dict:
        """Get diagnostic information."""
        # Build detailed device_commands info
        device_commands_detail = {}
        for device, commands in self.data.get("device_commands", {}).items():
            device_commands_detail[device] = {
                "count": len(commands),
                "command_ids": [cmd.get("id") for cmd in commands if cmd.get("id")],
                "commands_full": commands[:5],  # Show first 5 commands as sample
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
