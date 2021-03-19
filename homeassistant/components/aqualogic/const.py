"""Constants for the AquaLogic component."""

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 23
DEFAULT_PATH = "/dev/ttyUSB0"

DOMAIN = "aqualogic"
PROCESSOR = "aqualogic"
UPDATE_TOPIC = f"{DOMAIN}_update"
UNDO_UPDATE_LISTENER = "undo_update_listener"

PROTOCOL_SERIAL = "serial"
PROTOCOL_SOCKET = "socket"
