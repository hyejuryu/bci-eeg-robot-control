import time
from dataclasses import dataclass
from datetime import datetime

import serial

from bci_robot.serial_protocol import (
    AckMessage,
    ErrorMessage,
    ReadyMessage,
    parse_protocol_message,
)

@dataclass(frozen=True)
class SerialEvent:
    host_time_iso: str
    host_elapsed_ms: float
    case_id: str
    command_seq: int
    direction: str
    raw_message: str
    message_type: str
    command: str
    result: str
    actuator_mode: str
    commanded_angle_deg: int | None
    note: str


class SerialClient:
    def __init__(
        self,
        port: str,
        baud_rate: int,
        response_timeout_s: float,
        read_timeout_s: float = 0.1,
    ) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.response_timeout_s = response_timeout_s
        self.read_timeout_s = read_timeout_s

        self.events: list[SerialEvent] = []
        self.run_start_monotonic = time.monotonic()
        self.next_command_seq = 1
        self._connection: serial.Serial | None = None

    @property
    def is_open(self) -> bool:
        return (
            self._connection is not None
            and self._connection.is_open
        )

    def open(self) -> None:
        if self.is_open:
            return

        self._connection = serial.Serial(
            port=self.port,
            baudrate=self.baud_rate,
            timeout=self.read_timeout_s,
        )

    def close(self) -> None:
        if self._connection is None:
            return

        self._connection.close()
        self._connection = None

    def _append_event(
        self,
        *,
        case_id: str,
        command_seq: int,
        direction: str,
        raw_message: str,
        message_type: str,
        command: str = "",
        result: str = "",
        actuator_mode: str = "",
        commanded_angle_deg: int | None = None,
        note: str = "",
    ) -> None:
        self.events.append(
            SerialEvent(
                host_time_iso=(
                    datetime.now()
                    .astimezone()
                    .isoformat(timespec="milliseconds")
                ),
                host_elapsed_ms=round(
                    (
                        time.monotonic()
                        - self.run_start_monotonic
                    )
                    * 1000.0,
                    3,
                ),
                case_id=case_id,
                command_seq=command_seq,
                direction=direction,
                raw_message=raw_message,
                message_type=message_type,
                command=command,
                result=result,
                actuator_mode=actuator_mode,
                commanded_angle_deg=commanded_angle_deg,
                note=note,
            )
        )

    def wait_ready(
        self,
        *,
        timeout_s: float,
        case_id: str = "STARTUP",
    ) -> ReadyMessage:
        if (
            self._connection is None
            or not self._connection.is_open
        ):
            raise RuntimeError(
                "Serial port is not open."
            )

        deadline = time.monotonic() + timeout_s

        while time.monotonic() < deadline:
            raw_response = self._connection.readline()

            if not raw_response:
                continue

            line = raw_response.decode("ascii").strip()
            print(f"RX: {line}")

            message = parse_protocol_message(line)

            if not isinstance(message, ReadyMessage):
                raise RuntimeError(
                    "Expected READY during startup, "
                    f"received {type(message).__name__}."
                )

            self._append_event(
                case_id=case_id,
                command_seq=0,
                direction="RX",
                raw_message=line,
                message_type="READY",
                actuator_mode=message.actuator_mode,
                commanded_angle_deg=(
                    message.commanded_angle_deg
                ),
                note=(
                    "protocol_version="
                    f"{message.protocol_version}"
                ),
            )

            return message

        raise TimeoutError(
            "No READY message received within "
            f"{timeout_s} seconds."
        )

    def send_command(
        self,
        command: str,
        *,
        case_id: str,
    ) -> AckMessage | ErrorMessage:
        if (
            self._connection is None
            or not self._connection.is_open
        ):
            raise RuntimeError(
                "Serial port is not open."
            )

        command_seq = self.next_command_seq
        command_line = f"{command}\n"

        self._connection.write(
            command_line.encode("ascii")
        )
        self._connection.flush()

        print(f"TX: {command}")

        self._append_event(
            case_id=case_id,
            command_seq=command_seq,
            direction="TX",
            raw_message=command,
            message_type="COMMAND",
            command=command,
        )

        self.next_command_seq += 1

        deadline = (
            time.monotonic()
            + self.response_timeout_s
        )

        while time.monotonic() < deadline:
            raw_response = self._connection.readline()

            if not raw_response:
                continue

            line = raw_response.decode(
                "ascii"
            ).strip()

            print(f"RX: {line}")

            message = parse_protocol_message(line)

            if isinstance(message, AckMessage):
                self._append_event(
                    case_id=case_id,
                    command_seq=command_seq,
                    direction="RX",
                    raw_message=line,
                    message_type="ACK",
                    command=message.command,
                    result=message.result,
                    actuator_mode=message.actuator_mode,
                    commanded_angle_deg=(
                        message.commanded_angle_deg
                    ),
                )

                if message.command != command:
                    raise RuntimeError(
                        "ACK command mismatch: "
                        f"sent {command!r}, "
                        f"received "
                        f"{message.command!r}."
                    )

                return message

            if isinstance(message, ErrorMessage):
                self._append_event(
                    case_id=case_id,
                    command_seq=command_seq,
                    direction="RX",
                    raw_message=line,
                    message_type="ERR",
                    result=message.error_code,
                    actuator_mode=message.actuator_mode,
                    commanded_angle_deg=(
                        message.commanded_angle_deg
                    ),
                )

                return message

            if isinstance(message, ReadyMessage):
                self._append_event(
                    case_id=case_id,
                    command_seq=command_seq,
                    direction="RX",
                    raw_message=line,
                    message_type="READY",
                    actuator_mode=message.actuator_mode,
                    commanded_angle_deg=(
                        message.commanded_angle_deg
                    ),
                    note=(
                        "Unexpected READY while "
                        "waiting for command response"
                    ),
                )

                raise RuntimeError(
                    "Unexpected READY received while "
                    "waiting for ACK or ERR."
                )

        raise TimeoutError(
            "No ACK or ERR received within "
            f"{self.response_timeout_s} seconds "
            f"for command {command!r}."
        )