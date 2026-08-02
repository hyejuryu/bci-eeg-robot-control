from dataclasses import dataclass


PROTOCOL_VERSION = "S18_V0.1"
VALID_ACTUATOR_MODES = {
    "STOP",
    "OPEN",
    "CLOSE",
}

VALID_COMMANDS = {
    "OPEN",
    "CLOSE",
    "STOP",
}

VALID_COMMAND_RESULTS = {
    "APPLIED",
    "DUPLICATE",
    "REVERSED",
}

class ProtocolParseError(ValueError):
    """Raised when a serial protocol message is malformed."""


@dataclass(frozen=True)
class ReadyMessage:
    protocol_version: str
    actuator_mode: str
    commanded_angle_deg: int

@dataclass(frozen=True)
class AckMessage:
    command: str
    result: str
    actuator_mode: str
    commanded_angle_deg: int

@dataclass(frozen=True)
class ErrorMessage:
    error_code: str
    actuator_mode: str
    commanded_angle_deg: int


def parse_ready_message(line: str) -> ReadyMessage:
    fields = line.split(",")

    if len(fields) != 4:
        raise ProtocolParseError(
            f"READY message must contain 4 fields: {line!r}"
        )

    message_type, protocol_version, actuator_mode, angle_text = fields

    if message_type != "READY":
        raise ProtocolParseError(
            f"Expected READY message, received: {message_type!r}"
        )

    if protocol_version != PROTOCOL_VERSION:
        raise ProtocolParseError(
            f"Unexpected protocol version: {protocol_version!r}"
        )

    if actuator_mode not in VALID_ACTUATOR_MODES:
        raise ProtocolParseError(
            f"Invalid actuator mode: {actuator_mode!r}"
        )

    try:
        commanded_angle_deg = int(angle_text)
    except ValueError as exc:
        raise ProtocolParseError(
            f"Commanded angle must be an integer: {angle_text!r}"
        ) from exc

    return ReadyMessage(
        protocol_version=protocol_version,
        actuator_mode=actuator_mode,
        commanded_angle_deg=commanded_angle_deg,
    )

def parse_ack_message(line: str) -> AckMessage:
    fields = line.split(",")

    if len(fields) != 5:
        raise ProtocolParseError(
            f"ACK message must contain 5 fields: {line!r}"
        )

    (
        message_type,
        command,
        result,
        actuator_mode,
        angle_text,
    ) = fields

    if message_type != "ACK":
        raise ProtocolParseError(
            f"Expected ACK message, received: {message_type!r}"
        )

    if command not in VALID_COMMANDS:
        raise ProtocolParseError(
            f"Invalid command in ACK: {command!r}"
        )

    if result not in VALID_COMMAND_RESULTS:
        raise ProtocolParseError(
            f"Invalid command result: {result!r}"
        )

    if actuator_mode not in VALID_ACTUATOR_MODES:
        raise ProtocolParseError(
            f"Invalid actuator mode: {actuator_mode!r}"
        )

    try:
        commanded_angle_deg = int(angle_text)
    except ValueError as exc:
        raise ProtocolParseError(
            f"Commanded angle must be an integer: {angle_text!r}"
        ) from exc

    return AckMessage(
        command=command,
        result=result,
        actuator_mode=actuator_mode,
        commanded_angle_deg=commanded_angle_deg,
    )


def parse_error_message(line: str) -> ErrorMessage:
    fields = line.split(",")

    if len(fields) != 4:
        raise ProtocolParseError(
            f"ERR message must contain 4 fields: {line!r}"
        )

    (
        message_type,
        error_code,
        actuator_mode,
        angle_text,
    ) = fields

    if message_type != "ERR":
        raise ProtocolParseError(
            f"Expected ERR message, received: {message_type!r}"
        )

    if error_code != "INVALID_COMMAND":
        raise ProtocolParseError(
            f"Unexpected error code: {error_code!r}"
        )

    if actuator_mode not in VALID_ACTUATOR_MODES:
        raise ProtocolParseError(
            f"Invalid actuator mode: {actuator_mode!r}"
        )

    try:
        commanded_angle_deg = int(angle_text)
    except ValueError as exc:
        raise ProtocolParseError(
            f"Commanded angle must be an integer: {angle_text!r}"
        ) from exc

    return ErrorMessage(
        error_code=error_code,
        actuator_mode=actuator_mode,
        commanded_angle_deg=commanded_angle_deg,
    )


def parse_protocol_message(
    line: str,
) -> ReadyMessage | AckMessage | ErrorMessage:
    normalized_line = line.strip()

    if not normalized_line:
        raise ProtocolParseError(
            "Protocol message must not be empty."
        )

    message_type = normalized_line.split(",", maxsplit=1)[0]

    if message_type == "READY":
        return parse_ready_message(normalized_line)

    if message_type == "ACK":
        return parse_ack_message(normalized_line)

    if message_type == "ERR":
        return parse_error_message(normalized_line)

    raise ProtocolParseError(
        f"Unsupported message type: {message_type!r}"
    )