"""The AquaLogic integration."""
import asyncio
from datetime import timedelta
import logging
import threading
import time

from aqualogic.core import AquaLogic

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PATH, CONF_PORT, CONF_PROTOCOL
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PROTOCOL_SOCKET

UPDATE_TOPIC = f"{DOMAIN}_update"

PLATFORMS = ["sensor", "switch"]

_LOGGER = logging.getLogger(__name__)

RECONNECT_INTERVAL = timedelta(seconds=10)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AquaLogic component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up AquaLogic from a config entry."""

    processor = AquaLogicProcessor(hass, entry.data)
    hass.data[DOMAIN] = processor

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AquaLogicProcessor(threading.Thread):
    """AquaLogic event processor thread."""

    def __init__(self, hass, conf):
        """Initialize the data object."""
        super().__init__(daemon=True)
        self._hass = hass
        self._conf = conf
        self._shutdown = False
        self._panel = None

    def start_listen(self, event):
        """Start event-processing thread."""
        _LOGGER.debug("Event processing thread started")
        self.start()

    def shutdown(self, event):
        """Signal shutdown of processing event."""
        _LOGGER.debug("Event processing signaled exit")
        self._shutdown = True

    def data_changed(self, panel):
        """Aqualogic data changed callback."""
        self._hass.helpers.dispatcher.dispatcher_send(UPDATE_TOPIC)

    def run(self):
        """Event thread."""

        while True:
            self._panel = AquaLogic()

            if self._conf[CONF_PROTOCOL] == PROTOCOL_SOCKET:
                host = self._conf[CONF_HOST]
                port = self._conf[CONF_PORT]
                _LOGGER.info("Connecting to %s:%d", host, port)
                self._panel.connect_socket(host, port)
            else:
                path = self._conf[CONF_PATH]
                _LOGGER.info("Connecting to %s", path)
                self._panel.connect_serial(path)

            self._panel.process(self.data_changed)

            if self._shutdown:
                return

            _LOGGER.error("Connection lost")
            time.sleep(RECONNECT_INTERVAL.seconds)

    @property
    def panel(self):
        """Retrieve the AquaLogic object."""
        return self._panel
