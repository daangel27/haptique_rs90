"""Wake a sleeping RS90 up over the network.

Off its dock the RS90 sleeps and drops its MQTT connection. Any packet sent
to its IP address wakes the Wi-Fi chip up (the MAC address in a Wake-on-LAN
packet does not matter, and the RS90 uses a random MAC by default), but often
only after a few tries. So we send short bursts of UDP packets to its IP until
the RS90 reports `online` again over MQTT.
"""

from __future__ import annotations

import asyncio
import logging
import socket

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

WAKE_PORT = 9
# A Wake-on-LAN "magic packet"; the target MAC is irrelevant for the RS90.
MAGIC_PACKET = b"\xff" * 6 + b"\xff" * 6 * 16
BURST_SIZE = 3
BURST_GAP = 0.3
WAIT_PER_ATTEMPT = 3.0
DEFAULT_TIMEOUT = 20.0
# After waking up, give the RS90 time to resubscribe to its command topics.
WAKE_SETTLE = 4.0
# Gap between commands queued during a wake-up.
QUEUE_GAP = 0.3


def _send_burst(host: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for _ in range(BURST_SIZE):
            sock.sendto(MAGIC_PACKET, (host, WAKE_PORT))


async def async_wake(
    hass: HomeAssistant,
    host: str,
    online: asyncio.Event,
    timeout: float = DEFAULT_TIMEOUT,
) -> bool:
    """Send bursts to `host` until `online` is set or `timeout` expires."""
    if online.is_set():
        return True
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    attempt = 0
    while loop.time() < deadline:
        attempt += 1
        try:
            await hass.async_add_executor_job(_send_burst, host)
        except OSError as err:
            _LOGGER.warning("Could not send wake packets to %s: %s", host, err)
            return False
        try:
            remaining = max(0.0, deadline - loop.time())
            await asyncio.wait_for(online.wait(), min(WAIT_PER_ATTEMPT, remaining))
        except TimeoutError:
            await asyncio.sleep(BURST_GAP)
            continue
        _LOGGER.info("RS90 woke up after %d attempt(s)", attempt)
        return True
    _LOGGER.warning("RS90 at %s did not wake up within %.0f s", host, timeout)
    return False
