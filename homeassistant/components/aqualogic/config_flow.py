"""Config flow for AquaLogic."""
import logging
from socket import gaierror

from aqualogic.core import AquaLogic
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PATH, CONF_PORT, CONF_PROTOCOL
from homeassistant.core import callback

from .const import (  # pylint: disable=unused-import
    DEFAULT_HOST,
    DEFAULT_PATH,
    DEFAULT_PORT,
    DOMAIN,
    PROTOCOL_SERIAL,
    PROTOCOL_SOCKET,
)

_LOGGER = logging.getLogger(__name__)


class AquaLogicFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a AquaLogic config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize AquaLogic ConfigFlow."""
        self.protocol = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for AquaLogic."""
        return AquaLogicOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.protocol = user_input[CONF_PROTOCOL]
            return await self.async_step_protocol()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROTOCOL): vol.In(
                        [PROTOCOL_SOCKET, PROTOCOL_SERIAL]
                    ),
                }
            ),
        )

    async def async_step_protocol(self, user_input=None):
        """Handle AquaLogic protocol setup."""
        errors = {}
        if user_input is not None:
            if _device_already_added(
                self._async_current_entries(), user_input, self.protocol
            ):
                return self.async_abort(reason="already_configured")

            connection = {}

            controller = AquaLogic()

            try:
                if self.protocol == PROTOCOL_SOCKET:
                    host = connection[CONF_HOST] = user_input[CONF_HOST]
                    port = connection[CONF_PORT] = user_input[CONF_PORT]
                    title = f"{host}:{port}"
                    controller.connect_socket(host, port)
                if self.protocol == PROTOCOL_SERIAL:
                    path = connection[CONF_PATH] = user_input[CONF_PATH]
                    title = path
                    controller.connect_serial(path)

                return self.async_create_entry(
                    title=title, data={CONF_PROTOCOL: self.protocol, **connection}
                )
            except ConnectionRefusedError:
                errors["base"] = "cannot_connect"
            except gaierror:
                errors["base"] = "invalid_host"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during AquaLogic setup")
                errors["base"] = "unknown"

        if self.protocol == PROTOCOL_SOCKET:
            schema = vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                }
            )
        if self.protocol == PROTOCOL_SERIAL:
            schema = vol.Schema(
                {
                    vol.Required(CONF_PATH, default=DEFAULT_PATH): str,
                }
            )

        return self.async_show_form(
            step_id="protocol",
            data_schema=schema,
            errors=errors,
        )


class AquaLogicOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle AquaLogic options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize AquaLogic options flow."""
        pass


def _device_already_added(current_entries, user_input, protocol):
    """Determine if entry has already been added to HA."""
    user_host = user_input.get(CONF_HOST)
    user_port = user_input.get(CONF_PORT)
    user_path = user_input.get(CONF_PATH)

    for entry in current_entries:
        entry_host = entry.data.get(CONF_HOST)
        entry_port = entry.data.get(CONF_PORT)
        entry_path = entry.data.get(CONF_PATH)

        if protocol == PROTOCOL_SOCKET:
            if user_host == entry_host and user_port == entry_port:
                return True

        if protocol == PROTOCOL_SERIAL:
            if user_path == entry_path:
                return True

    return False
