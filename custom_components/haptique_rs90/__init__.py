"""The Haptique RS90 Remote integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import HaptiqueRS90Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BUTTON,  # RGB ring light control - First in controls section
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,  # Macros as switches (on/off state visible)
]


def _coordinator_for_device(
    hass: HomeAssistant, device_id: str
) -> HaptiqueRS90Coordinator:
    """Use the HA device selector and report invalid calls to the caller."""
    device = dr.async_get(hass).async_get(device_id)
    if device:
        for entry_id in device.config_entries:
            if coordinator := hass.data.get(DOMAIN, {}).get(entry_id):
                return coordinator
    raise ServiceValidationError("Configured RS90 device not found")


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register existing actions and explicit sequence/state-query actions."""
    remote = {vol.Required("rs90_id"): cv.string}
    action = {vol.Optional("action", default="on"): vol.In(("on", "off"))}

    async def trigger_macro(call):
        coordinator = _coordinator_for_device(hass, call.data["rs90_id"])
        await coordinator.async_trigger_macro(
            call.data["rs90_macro_id"], call.data["action"]
        )

    async def trigger_sequence(call):
        coordinator = _coordinator_for_device(hass, call.data["rs90_id"])
        await coordinator.async_trigger_target(
            "sequence", call.data["rs90_sequence_id"], call.data["action"]
        )

    async def query_status(call):
        coordinator = _coordinator_for_device(hass, call.data["rs90_id"])
        await coordinator.async_query_status(
            call.data["target_kind"], call.data["target_id"]
        )

    async def device_command(call):
        coordinator = _coordinator_for_device(hass, call.data["rs90_id"])
        device_id = call.data["rs90_device_id"]
        device = next(
            (item for item in coordinator.data["devices"] if item["id"] == device_id),
            None,
        )
        if device is None:
            raise ServiceValidationError("Configured device ID not found")
        await coordinator.async_trigger_device_command(
            device["name"], call.data["command_name"]
        )

    async def refresh(call):
        await _coordinator_for_device(
            hass, call.data["rs90_id"]
        ).async_force_refresh_lists()

    async def rgb(call):
        await _coordinator_for_device(
            hass, call.data["rs90_id"]
        ).async_control_led_light("on", call.data["duration"])

    async def launch_app(call):
        await _coordinator_for_device(hass, call.data["rs90_id"]).async_launch_app(
            call.data["app_package_id"]
        )

    services = {
        "launch_app": (
            launch_app,
            {**remote, vol.Required("app_package_id"): cv.string},
        ),
        "trigger_macro": (
            trigger_macro,
            {**remote, **action, vol.Required("rs90_macro_id"): cv.string},
        ),
        "trigger_sequence": (
            trigger_sequence,
            {**remote, **action, vol.Required("rs90_sequence_id"): cv.string},
        ),
        "query_status": (
            query_status,
            {
                **remote,
                vol.Required("target_kind"): vol.In(("macro", "sequence")),
                vol.Required("target_id"): cv.string,
            },
        ),
        "trigger_device_command": (
            device_command,
            {
                **remote,
                vol.Required("rs90_device_id"): cv.string,
                vol.Required("command_name"): cv.string,
            },
        ),
        "refresh_lists": (refresh, remote),
        "trigger_rgb_light": (
            rgb,
            {
                **remote,
                vol.Optional("duration", default=5): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=10)
                ),
            },
        ),
    }
    for name, (handler, fields) in services.items():
        if not hass.services.has_service(DOMAIN, name):
            hass.services.async_register(
                DOMAIN, name, handler, schema=vol.Schema(fields)
            )


async def _async_cleanup_old_macro_info_sensors(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Remove old macro info sensors and device list sensor (migration v1.5.0 -> v1.6.0)."""
    from homeassistant.helpers import entity_registry as er

    entity_registry = er.async_get(hass)

    _LOGGER.info(
        "=== Starting cleanup of old sensors for entry: %s ===", entry.entry_id
    )

    # Find all macro info sensors and device list sensor for this remote
    entities_to_remove = []
    all_entities = []

    for entity in entity_registry.entities.values():
        if entity.platform == DOMAIN and entity.config_entry_id == entry.entry_id:
            all_entities.append(f"{entity.entity_id} (unique_id: {entity.unique_id})")

            # Check if it's a macro info sensor (unique_id contains "macro_info_")
            # or device list sensor (unique_id ends with "_device_list")
            if entity.unique_id:
                if "macro_info_" in entity.unique_id or entity.unique_id.endswith(
                    "_device_list"
                ):
                    entities_to_remove.append(entity.entity_id)
                    _LOGGER.info(
                        "Found old sensor to remove: %s (unique_id: %s)",
                        entity.entity_id,
                        entity.unique_id,
                    )

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
        _LOGGER.info(
            "=== Migration complete: Removed %d old sensors ===",
            len(entities_to_remove),
        )
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

    # Register device
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data["remote_id"])},
        name=entry.data.get("name", f"Haptique RS90 {entry.data['remote_id'][:8]}"),
        manufacturer="Haptique",
        model="RS90",
        sw_version="1.0",
    )

    # Store HA device ID in coordinator for event firing
    coordinator.device_id = device_entry.id

    # Subscribe to MQTT topics and start coordinator
    try:
        await coordinator.async_config_entry_first_refresh()
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except BaseException:
        await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id, None)
        raise

    # Cleanup old sensors AFTER platforms are loaded
    await _async_cleanup_old_macro_info_sensors(hass, entry)

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
