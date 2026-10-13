"""Macro/sequence switches with stable identities and confirmed MQTT state."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_REMOTE_ID, DOMAIN
from .coordinator import HaptiqueRS90Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Keep registry entries even when independent snapshots temporarily omit them."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    registry = er.async_get(hass)
    prefix = f"{entry.data[CONF_REMOTE_ID]}_macro_"
    registered = {
        entity.unique_id: entity
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        if entity.domain == "switch" and entity.platform == DOMAIN
    }
    owners = {
        unique_id: (entity.capabilities or {}).get("haptique_target_kind")
        for unique_id, entity in registered.items()
    }
    legacy_ids = {
        unique_id[len(prefix) :]
        for unique_id, entity in registered.items()
        if unique_id.startswith(prefix)
        and (entity.capabilities or {}).get("haptique_legacy_macro") is not False
    }
    entities: dict[str, HaptiqueRS90MacroSwitch] = {}

    @callback
    def reconcile() -> None:
        for record in coordinator.data["macros"]:
            if "type" in record:
                legacy_ids.discard(record["id"])
            else:
                legacy_ids.add(record["id"])
        additions = []
        for (kind, target_id), record in coordinator.targets.items().items():
            identity_kind = kind
            old_unique_id = f"{prefix}{target_id}"
            if owners.get(old_unique_id) == "sequence":
                # Once migrated, the historical identity permanently belongs
                # to that sequence, including across restart and ID conflicts.
                identity_kind = "macro" if kind == "sequence" else "real_macro"
            elif kind == "sequence" and target_id in legacy_ids:
                # Wait for macro/list before deciding whether a registered identity
                # belongs to a real macro or to a migrated legacy sequence.
                if "macro" not in coordinator.targets.seen:
                    continue
                own_id = f"{entry.data[CONF_REMOTE_ID]}_sequence_{target_id}"
                if (
                    not coordinator.targets.target("macro", target_id)
                    and own_id not in entities
                    and not registry.async_get_entity_id("switch", DOMAIN, own_id)
                ):
                    identity_kind = "macro"
            unique_id = f"{entry.data[CONF_REMOTE_ID]}_{identity_kind}_{target_id}"
            if unique_id not in entities:
                entity = HaptiqueRS90MacroSwitch(
                    coordinator,
                    entry,
                    target_id,
                    record["name"],
                    kind,
                    identity_kind,
                    kind == "macro" and "type" not in record,
                )
                entities[unique_id] = entity
                additions.append(entity)
            else:
                entity = entities[unique_id]
                entity._target_kind = kind
                entity._macro_name = record["name"]
                entity._legacy = kind == "macro" and "type" not in record
            owners[unique_id] = kind
            if registry_id := registry.async_get_entity_id("switch", DOMAIN, unique_id):
                existing = registry.async_get(registry_id)
                capabilities = {
                    **(existing.capabilities or {}),
                    **entity.capability_attributes,
                }
                if capabilities != existing.capabilities:
                    registry.async_update_entity(registry_id, capabilities=capabilities)
        if additions:
            async_add_entities(additions)

    reconcile()
    entry.async_on_unload(coordinator.async_add_listener(reconcile))


class HaptiqueRS90MacroSwitch(CoordinatorEntity, SwitchEntity):
    """An ON/OFF execution state, not a measurement of equipment power."""

    def __init__(
        self,
        coordinator: HaptiqueRS90Coordinator,
        entry: ConfigEntry,
        macro_id: str,
        macro_name: str,
        target_kind: str = "macro",
        identity_kind: str = "macro",
        legacy: bool = False,
    ) -> None:
        super().__init__(coordinator)
        self._switch_id = macro_id
        self._macro_name = macro_name
        self._target_kind = target_kind
        self._legacy = legacy
        self._attr_unique_id = (
            f"{entry.data[CONF_REMOTE_ID]}_{identity_kind}_{macro_id}"
        )
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.data[CONF_REMOTE_ID])}}

    @property
    def capability_attributes(self) -> dict[str, Any]:
        """Persist migration ownership without changing config-entry settings."""
        return {
            "haptique_target_kind": self._target_kind,
            "haptique_legacy_macro": self._legacy,
        }

    @property
    def name(self) -> str:
        return self._macro_name

    @property
    def available(self) -> bool:
        return (
            self.coordinator.data.get("status") == "online"
            and self.coordinator.targets.target(self._target_kind, self._switch_id)
            is not None
            and not self.coordinator.targets.conflicting(self._switch_id)
        )

    @property
    def is_on(self) -> bool | None:
        state = self.coordinator.targets.state(self._target_kind, self._switch_id)
        return None if state is None else state == "on"

    @property
    def icon(self) -> str:
        return "mdi:stop-circle" if self.is_on else "mdi:play-circle"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        target = (
            self.coordinator.targets.target(self._target_kind, self._switch_id) or {}
        )
        attributes = {
            "rs90_macro_id": self._switch_id,
            "macro_name": self._macro_name,
            "target_id": self._switch_id,
            "target_kind": self._target_kind,
            "current_state": self.coordinator.targets.state(
                self._target_kind, self._switch_id
            ),
            "last_result": self.coordinator.targets.result(
                self._target_kind, self._switch_id
            ),
        }
        if self._target_kind == "sequence":
            attributes["rs90_sequence_id"] = self._switch_id
        if "supportsOff" in target:
            attributes["supports_off"] = target["supportsOff"]
        if self.coordinator.targets.conflicting(self._switch_id):
            attributes["inventory_error"] = "target_id_conflict"
        return attributes

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_trigger_target(
            self._target_kind, self._switch_id, "on"
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_trigger_target(
            self._target_kind, self._switch_id, "off"
        )
