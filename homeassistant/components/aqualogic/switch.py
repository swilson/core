"""Support for AquaLogic switches."""
from aqualogic.core import States

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN, PROCESSOR, UPDATE_TOPIC

SWITCH_TYPES = {
    "lights": ["Lights", States.LIGHTS],
    "filter": ["Filter", States.FILTER],
    "filter_low_speed": ["Filter Low Speed", States.FILTER_LOW_SPEED],
    "pool": ["Pool", States.POOL],
    "spa": ["Spa", States.SPA],
    "aux_1": ["Aux 1", States.AUX_1],
    "aux_2": ["Aux 2", States.AUX_2],
    "aux_3": ["Aux 3", States.AUX_3],
    "aux_4": ["Aux 4", States.AUX_4],
    "aux_5": ["Aux 5", States.AUX_5],
    "aux_6": ["Aux 6", States.AUX_6],
    "aux_7": ["Aux 7", States.AUX_7],
    "aux_8": ["Aux 8", States.AUX_8],
    "aux_9": ["Aux 9", States.AUX_9],
    "aux_10": ["Aux 10", States.AUX_10],
    "aux_11": ["Aux 11", States.AUX_11],
    "aux_12": ["Aux 12", States.AUX_12],
    "aux_13": ["Aux 13", States.AUX_13],
    "aux_14": ["Aux 14", States.AUX_14],
    "valve_3": ["Valve 3", States.VALVE_3],
    "valve_4": ["Valve 4", States.VALVE_4],
    "heater_auto_mode": ["Heater Auto Mode", States.HEATER_AUTO_MODE],
    "service": ["Service", States.SERVICE],
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the switches."""
    switches = []

    data = hass.data[DOMAIN][config_entry.entry_id]
    processor = data[PROCESSOR]

    for switch_type in SWITCH_TYPES:
        switches.append(AquaLogicSwitch(processor, switch_type))

    async_add_entities(switches)


class AquaLogicSwitch(SwitchEntity):
    """Switch implementation for the AquaLogic component."""

    def __init__(self, processor, switch_type):
        """Initialize switch."""
        self._processor = processor
        self._type = switch_type

    @property
    def name(self):
        """Return the name of the switch."""
        return f"AquaLogic {SWITCH_TYPES[self._type][0]}"

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        panel = self._processor.panel
        if panel is None:
            return False
        state = panel.get_state(SWITCH_TYPES[self._type][1])
        return state

    def turn_on(self, **kwargs):
        """Turn the device on."""
        panel = self._processor.panel
        if panel is None:
            return
        panel.set_state(SWITCH_TYPES[self._type][1], True)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        panel = self._processor.panel
        if panel is None:
            return
        panel.set_state(SWITCH_TYPES[self._type][1], False)

    async def async_added_to_hass(self):
        """Register callbacks."""
        self.async_on_remove(
            self.hass.helpers.dispatcher.async_dispatcher_connect(
                UPDATE_TOPIC, self.async_write_ha_state
            )
        )
