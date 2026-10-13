"""Validated Standard MQTT targets and owned feedback subscriptions."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)
TargetKey = tuple[str, str]
INVENTORIES = {"macro": "macros", "sequence": "sequences"}


def valid_reference(value: Any) -> bool:
    """A stable ID must fit one literal MQTT topic level."""
    return (
        isinstance(value, str)
        and bool(value.strip())
        and not any(char in value for char in "/+#\x00")
    )


def parse_inventory(payload: str) -> list[dict[str, Any]]:
    """Reject a whole invalid snapshot instead of deleting existing entities."""
    records = json.loads(payload)
    if not isinstance(records, list):
        raise ValueError("Inventory must be an array")
    result = []
    ids = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Inventory record must be an object")
        target_id = record.get("id") or record.get("Id")
        name = record.get("name")
        if (
            not valid_reference(target_id)
            or not isinstance(name, str)
            or not name.strip()
        ):
            raise ValueError("Inventory requires a topic-safe ID and a name")
        if target_id in ids:
            raise ValueError("Duplicate inventory ID")
        ids.add(target_id)
        normalized = {"id": target_id, "name": name}
        for field in ("type", "supportsOff", "source", "category"):
            if field in record:
                normalized[field] = record[field]
        if "supportsOff" in normalized and not isinstance(
            normalized["supportsOff"], bool
        ):
            raise ValueError("supportsOff must be boolean")
        if "type" in normalized and normalized["type"] != "macro":
            raise ValueError("Unsupported macro type")
        result.append(normalized)
    return result


class TargetManager:
    """Keep execution state separate from commands and display names."""

    def __init__(self, coordinator) -> None:
        self.coordinator = coordinator
        self.seen: set[str] = set()
        self._subscriptions: dict[str, Callable[[], None]] = {}
        self._states: dict[TargetKey, str | None] = {}
        self._results: dict[TargetKey, dict[str, str]] = {}
        self._canonical_received: set[TargetKey] = set()
        self._known: set[TargetKey] = set()
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self._dirty = False
        self._closed = False

    def items(self) -> dict[TargetKey, dict[str, Any]]:
        """A legacy macro which moves to sequence inventory is one target."""
        data = self.coordinator.data
        sequence_ids = {record["id"] for record in data["sequences"]}
        return {
            (kind, record["id"]): record
            for kind, field in INVENTORIES.items()
            for record in data[field]
            if not (
                kind == "macro"
                and "type" not in record
                and record["id"] in sequence_ids
            )
        }

    def conflicting(self, target_id: str) -> bool:
        items = self.items()
        return ("macro", target_id) in items and ("sequence", target_id) in items

    def target(self, kind: str, target_id: str) -> dict[str, Any] | None:
        return self.items().get((kind, target_id))

    def require(self, kind: str, target_id: str) -> dict[str, Any]:
        if self._closed:
            raise HomeAssistantError("Remote integration is unloaded")
        if kind not in INVENTORIES or not (target := self.target(kind, target_id)):
            raise HomeAssistantError("Unknown macro or sequence ID")
        if self.conflicting(target_id):
            raise HomeAssistantError("Macro/sequence inventory conflict for this ID")
        return target

    def state(self, kind: str, target_id: str) -> str | None:
        if not self.target(kind, target_id) or self.conflicting(target_id):
            return None
        return self._states.get((kind, target_id))

    def result(self, kind: str, target_id: str) -> dict[str, str] | None:
        return self._results.get((kind, target_id))

    @callback
    def update_inventory(self, kind: str, records: list[dict[str, Any]]) -> None:
        if self._closed:
            return
        self.coordinator.data[INVENTORIES[kind]] = records
        self.seen.add(kind)
        current = self.items()
        for key in set(self._states) | set(self._results) | self._canonical_received:
            if key not in current or self.conflicting(key[1]):
                self._states.pop(key, None)
                self._results.pop(key, None)
                self._canonical_received.discard(key)
        self._publish_state()
        self._dirty = True
        if self._task is None or self._task.done():
            self._task = self.coordinator._create_task(self._run_reconcile())

    async def _run_reconcile(self) -> None:
        while self._dirty and not self._closed:
            self._dirty = False
            await self.async_reconcile()

    def _routes(self) -> dict[str, tuple[TargetKey, bool]]:
        routes = {}
        items = self.items()
        for key, record in items.items():
            kind, target_id = key
            if self.conflicting(target_id):
                continue
            # A sequence requested by name publishes a historical macro alias.
            # Without request IDs, that alias is indistinguishable from the
            # real macro's canonical feedback when the name equals its ID.
            unsafe_id = kind == "macro" and any(
                other_kind == "sequence" and item["name"] == target_id
                for (other_kind, _), item in items.items()
            )
            references = [] if unsafe_id else [(target_id, True)]
            name = record["name"]
            same_name = [other for other, item in items.items() if item["name"] == name]
            if (
                valid_reference(name)
                and name != target_id
                and len(same_name) == 1
                and (kind, name) not in items
                and ("sequence", name) not in items
            ):
                references.append((name, False))
            for reference, canonical in references:
                for suffix in ("status", "result"):
                    topic = f"{self.coordinator.base_topic}/{kind}/{reference}/{suffix}"
                    routes[topic] = (key, canonical)
        return routes

    async def async_reconcile(self) -> None:
        """Serialize list updates and subscribe before requesting feedback."""
        async with self._lock:
            if self._closed:
                return
            wanted = self._routes()
            for topic in set(self._subscriptions) - wanted.keys():
                self._subscriptions.pop(topic)()
            for topic in wanted.keys() - self._subscriptions.keys():

                @callback
                def received(msg, topic=topic):
                    route = self._routes().get(topic)
                    if not self._closed and route:
                        self._handle_feedback(topic, route, msg.payload)

                unsubscribe = await mqtt.async_subscribe(
                    self.coordinator.hass, topic, received, qos=0
                )
                if self._closed:
                    unsubscribe()
                    return
                self._subscriptions[topic] = unsubscribe
            current = {key for key in self.items() if not self.conflicting(key[1])}
            newly_discovered = current - self._known
            self._known = current
            for kind, target_id in newly_discovered:
                if not self.conflicting(target_id):
                    await self.async_query(kind, target_id)

    @callback
    def _handle_feedback(
        self, topic: str, route: tuple[TargetKey, bool], payload: str
    ) -> None:
        key, canonical = route
        if topic.endswith("/status"):
            state = payload.strip().upper()
            if state not in ("ON", "OFF", "UNKNOWN") or (
                not canonical
                and key in self._canonical_received
                and not (key[0] == "macro" and "type" not in self.require(*key))
            ):
                return
            if canonical:
                self._canonical_received.add(key)
            self._states[key] = None if state == "UNKNOWN" else state.lower()
        else:
            try:
                result = json.loads(payload)
            except (ValueError, TypeError):
                return
            if not isinstance(result, dict) or result.get("status") not in (
                "executed",
                "skipped",
                "rejected",
                "failed",
            ):
                return
            self._results[key] = {
                field: result[field]
                for field in ("status", "error")
                if isinstance(result.get(field), str)
            }
        self._publish_state()

    def _publish_state(self) -> None:
        data = self.coordinator.data
        for kind, field in INVENTORIES.items():
            data[f"{kind}_states"] = {
                record["name"]: self.state(kind, target_id)
                for (item_kind, target_id), record in self.items().items()
                if item_kind == kind
            }
        self.coordinator.async_set_updated_data(data)

    async def async_query(self, kind: str, target_id: str) -> None:
        self.require(kind, target_id)
        await mqtt.async_publish(
            self.coordinator.hass,
            f"{self.coordinator.base_topic}/{kind}/{target_id}/currentstatus",
            "",
            qos=0,
            retain=False,
        )

    async def async_query_all(self) -> None:
        await self.async_reconcile()
        for kind, target_id in self.items():
            if not self.conflicting(target_id):
                await self.async_query(kind, target_id)

    async def async_close(self) -> None:
        self._closed = True
        if self._task and not self._task.done():
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
        for unsubscribe in self._subscriptions.values():
            unsubscribe()
        self._subscriptions.clear()
