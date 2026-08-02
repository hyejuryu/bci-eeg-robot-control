import csv
import math
import time
from dataclasses import dataclass
from pathlib import Path

from bci_robot.serial_client import (
    SerialClient,
    SerialEvent,
)
from bci_robot.serial_protocol import (
    AckMessage,
    ErrorMessage,
    ReadyMessage,
)

PORT = "COM4"
BAUD_RATE = 9600
READY_TIMEOUT_S = 3.0
RESPONSE_TIMEOUT_S = 1.0

EXPECTED_PROTOCOL_VERSION = "S18_V0.1"
EXPECTED_STARTUP_MODE = "STOP"
EXPECTED_STARTUP_ANGLE_DEG = 90

CLOSE_ENDPOINT_DEG = 60
OPEN_ENDPOINT_DEG = 120

MOTION_STEP_DEG = 2
MOTION_UPDATE_INTERVAL_S = 0.05
ENDPOINT_WAIT_MARGIN_S = 0.2

V06_OPEN_RUN_S = 0.8
V06_FREEZE_CONFIRM_WAIT_S = 0.5

V08_DIRECTION_RUN_S = 0.9

VALIDATION_SUMMARY_PATH = Path(
    "results/session-18/session18_serial_validation_summary.csv"
)

SERIAL_EVENT_LOG_PATH = Path(
    "results/session-18/session18_serial_event_log.csv"
)

@dataclass(frozen=True)
class ValidationResult:
    case_id: str
    case_name: str
    status: str
    observed: str


def save_validation_summary(
    validation_results: list[ValidationResult],
) -> None:
    VALIDATION_SUMMARY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "case_id",
        "case_name",
        "status",
        "observed",
    ]

    with VALIDATION_SUMMARY_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in validation_results:
            writer.writerow(
                {
                    "case_id": result.case_id,
                    "case_name": result.case_name,
                    "status": result.status,
                    "observed": result.observed,
                }
            )


def save_serial_events(
    serial_events: list[SerialEvent],
) -> None:
    SERIAL_EVENT_LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "host_time_iso",
        "host_elapsed_ms",
        "case_id",
        "command_seq",
        "direction",
        "raw_message",
        "message_type",
        "command",
        "result",
        "actuator_mode",
        "commanded_angle_deg",
        "note",
    ]

    with SERIAL_EVENT_LOG_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for event in serial_events:
            writer.writerow(
                {
                    "host_time_iso": event.host_time_iso,
                    "host_elapsed_ms": event.host_elapsed_ms,
                    "case_id": event.case_id,
                    "command_seq": event.command_seq,
                    "direction": event.direction,
                    "raw_message": event.raw_message,
                    "message_type": event.message_type,
                    "command": event.command,
                    "result": event.result,
                    "actuator_mode": event.actuator_mode,
                    "commanded_angle_deg": (
                        event.commanded_angle_deg
                    ),
                    "note": event.note,
                }
            )


def calculate_motion_wait_s(
    start_angle_deg: int,
    target_angle_deg: int,
) -> float:
    required_updates = math.ceil(
        abs(target_angle_deg - start_angle_deg)
        / MOTION_STEP_DEG
    )

    return (
        required_updates * MOTION_UPDATE_INTERVAL_S
        + ENDPOINT_WAIT_MARGIN_S
    )


def validate_ready_message(
    ready_message: ReadyMessage,
) -> ValidationResult:
    checks = [
        (
            ready_message.protocol_version
            == EXPECTED_PROTOCOL_VERSION
        ),
        (
            ready_message.actuator_mode
            == EXPECTED_STARTUP_MODE
        ),
        (
            ready_message.commanded_angle_deg
            == EXPECTED_STARTUP_ANGLE_DEG
        ),
    ]

    status = "PASS" if all(checks) else "FAIL"

    observed = (
        f"protocol_version="
        f"{ready_message.protocol_version}; "
        f"startup_mode="
        f"{ready_message.actuator_mode}; "
        f"startup_angle="
        f"{ready_message.commanded_angle_deg}"
    )

    return ValidationResult(
        case_id="V02",
        case_name="Startup READY handshake",
        status=status,
        observed=observed,
    )


def run_invalid_command_case(
    client: SerialClient,
    ready_message: ReadyMessage,
) -> ValidationResult:

    invalid_response = client.send_command(
        "INVALID",
        case_id="V09",
    )

    if not isinstance(invalid_response, ErrorMessage):
        return ValidationResult(
            case_id="V09",
            case_name="Invalid command handling",
            status="FAIL",
            observed=(
                "INVALID command did not return "
                "an ErrorMessage."
            ),
        )

    stop_response = client.send_command(
        "STOP",
        case_id="V09",
    )

    if not isinstance(stop_response, AckMessage):
        return ValidationResult(
            case_id="V09",
            case_name="Invalid command handling",
            status="FAIL",
            observed=(
                "STOP recovery command did not return "
                "an AckMessage."
            ),
        )

    checks = [
        invalid_response.error_code == "INVALID_COMMAND",
        invalid_response.actuator_mode
        == ready_message.actuator_mode,
        invalid_response.commanded_angle_deg
        == ready_message.commanded_angle_deg,
        stop_response.command == "STOP",
        stop_response.result == "DUPLICATE",
        stop_response.actuator_mode
        == ready_message.actuator_mode,
        stop_response.commanded_angle_deg
        == ready_message.commanded_angle_deg,
    ]

    status = "PASS" if all(checks) else "FAIL"

    observed = (
        f"error={invalid_response.error_code}; "
        f"error_mode={invalid_response.actuator_mode}; "
        f"error_angle={invalid_response.commanded_angle_deg}; "
        f"recovery_result={stop_response.result}; "
        f"recovery_mode={stop_response.actuator_mode}; "
        f"recovery_angle={stop_response.commanded_angle_deg}"
    )

    return ValidationResult(
        case_id="V09",
        case_name="Invalid command handling",
        status=status,
        observed=observed,
    )


def run_stop_freeze_case(
    client: SerialClient,
) -> ValidationResult:
    close_setup_response = client.send_command(
        "CLOSE",
        case_id="V06",
    )

    if not isinstance(close_setup_response, AckMessage):
        return ValidationResult(
            case_id="V06",
            case_name="STOP commanded-angle freeze",
            status="FAIL",
            observed=(
                "CLOSE setup command did not return "
                "an AckMessage."
            ),
        )

    close_wait_s = calculate_motion_wait_s(
        close_setup_response.commanded_angle_deg,
        CLOSE_ENDPOINT_DEG,
    )
    time.sleep(close_wait_s)

    setup_stop_response = client.send_command(
        "STOP",
        case_id="V06",
    )

    if not isinstance(setup_stop_response, AckMessage):
        return ValidationResult(
            case_id="V06",
            case_name="STOP commanded-angle freeze",
            status="FAIL",
            observed=(
                "Endpoint setup STOP did not return "
                "an AckMessage."
            ),
        )

    open_response = client.send_command(
        "OPEN",
        case_id="V06",
    )

    if not isinstance(open_response, AckMessage):
        return ValidationResult(
            case_id="V06",
            case_name="STOP commanded-angle freeze",
            status="FAIL",
            observed="OPEN command did not return an AckMessage.",
        )

    time.sleep(V06_OPEN_RUN_S)

    first_stop_response = client.send_command(
        "STOP",
        case_id="V06",
    )

    if not isinstance(first_stop_response, AckMessage):
        return ValidationResult(
            case_id="V06",
            case_name="STOP commanded-angle freeze",
            status="FAIL",
            observed="First validation STOP did not return an AckMessage.",
        )

    time.sleep(V06_FREEZE_CONFIRM_WAIT_S)

    second_stop_response = client.send_command(
        "STOP",
        case_id="V06",
    )

    if not isinstance(second_stop_response, AckMessage):
        return ValidationResult(
            case_id="V06",
            case_name="STOP commanded-angle freeze",
            status="FAIL",
            observed="Second validation STOP did not return an AckMessage.",
        )

    checks = [
        setup_stop_response.command == "STOP",
        setup_stop_response.actuator_mode == "STOP",
        (
            setup_stop_response.commanded_angle_deg
            == CLOSE_ENDPOINT_DEG
        ),
        open_response.command == "OPEN",
        open_response.result == "APPLIED",
        open_response.actuator_mode == "OPEN",
        first_stop_response.command == "STOP",
        first_stop_response.result == "APPLIED",
        first_stop_response.actuator_mode == "STOP",
        second_stop_response.command == "STOP",
        second_stop_response.result == "DUPLICATE",
        second_stop_response.actuator_mode == "STOP",
        (
            first_stop_response.commanded_angle_deg
            == second_stop_response.commanded_angle_deg
        ),
        (
            first_stop_response.commanded_angle_deg
            > setup_stop_response.commanded_angle_deg
        ),
    ]

    status = "PASS" if all(checks) else "FAIL"

    observed = (
        f"setup_angle={setup_stop_response.commanded_angle_deg}; "
        f"open_run_s={V06_OPEN_RUN_S:.2f}; "
        f"first_stop_angle="
        f"{first_stop_response.commanded_angle_deg}; "
        f"second_stop_angle="
        f"{second_stop_response.commanded_angle_deg}; "
        f"freeze_wait_s={V06_FREEZE_CONFIRM_WAIT_S:.2f}"
    )

    return ValidationResult(
        case_id="V06",
        case_name="STOP commanded-angle freeze",
        status=status,
        observed=observed,
    )


def run_direction_reversal_case(
    client: SerialClient,
) -> ValidationResult:
    open_setup_response = client.send_command(
        "OPEN",
        case_id="V08",
    )

    if not isinstance(open_setup_response, AckMessage):
        return ValidationResult(
            case_id="V08",
            case_name="Direction reversal",
            status="FAIL",
            observed=(
                "OPEN setup command did not return "
                "an AckMessage."
            ),
        )

    open_wait_s = calculate_motion_wait_s(
        open_setup_response.commanded_angle_deg,
        OPEN_ENDPOINT_DEG,
    )
    time.sleep(open_wait_s)

    setup_stop_response = client.send_command(
        "STOP",
        case_id="V08",
    )

    if not isinstance(setup_stop_response, AckMessage):
        return ValidationResult(
            case_id="V08",
            case_name="Direction reversal",
            status="FAIL",
            observed=(
                "Endpoint setup STOP did not return "
                "an AckMessage."
            ),
        )

    close_response = client.send_command(
        "CLOSE",
        case_id="V08",
    )

    if not isinstance(close_response, AckMessage):
        return ValidationResult(
            case_id="V08",
            case_name="Direction reversal",
            status="FAIL",
            observed="CLOSE command did not return an AckMessage.",
        )

    time.sleep(V08_DIRECTION_RUN_S)

    reversal_response = client.send_command(
        "OPEN",
        case_id="V08",
    )

    if not isinstance(reversal_response, AckMessage):
        return ValidationResult(
            case_id="V08",
            case_name="Direction reversal",
            status="FAIL",
            observed=(
                "OPEN reversal command did not return "
                "an AckMessage."
            ),
        )

    time.sleep(V08_DIRECTION_RUN_S)

    post_reversal_stop_response = client.send_command(
        "STOP",
        case_id="V08",
    )

    if not isinstance(post_reversal_stop_response, AckMessage):
        return ValidationResult(
            case_id="V08",
            case_name="Direction reversal",
            status="FAIL",
            observed=(
                "Post-reversal STOP did not return "
                "an AckMessage."
            ),
        )

    checks = [
        setup_stop_response.commanded_angle_deg
        == OPEN_ENDPOINT_DEG,
        close_response.command == "CLOSE",
        close_response.result == "APPLIED",
        close_response.actuator_mode == "CLOSE",
        reversal_response.command == "OPEN",
        reversal_response.result == "REVERSED",
        reversal_response.actuator_mode == "OPEN",
        (
            reversal_response.commanded_angle_deg
            < close_response.commanded_angle_deg
        ),
        post_reversal_stop_response.command == "STOP",
        post_reversal_stop_response.result == "APPLIED",
        post_reversal_stop_response.actuator_mode == "STOP",
        (
            post_reversal_stop_response.commanded_angle_deg
            > reversal_response.commanded_angle_deg
        ),
    ]

    status = "PASS" if all(checks) else "FAIL"

    observed = (
        f"close_start_angle="
        f"{close_response.commanded_angle_deg}; "
        f"close_run_s={V08_DIRECTION_RUN_S:.2f}; "
        f"reversal_angle="
        f"{reversal_response.commanded_angle_deg}; "
        f"post_reversal_angle="
        f"{post_reversal_stop_response.commanded_angle_deg}; "
        f"final_mode="
        f"{post_reversal_stop_response.actuator_mode}"
    )

    return ValidationResult(
        case_id="V08",
        case_name="Direction reversal",
        status=status,
        observed=observed,
    )


def run_open_endpoint_case(
    client: SerialClient,
) -> ValidationResult:
    close_setup_response = client.send_command(
        "CLOSE",
        case_id="V10-OPEN",
    )

    if not isinstance(close_setup_response, AckMessage):
        return ValidationResult(
            case_id="V10-OPEN",
            case_name="OPEN software endpoint snapshot",
            status="FAIL",
            observed=(
                "CLOSE setup command did not return "
                "an AckMessage."
            ),
        )

    close_wait_s = calculate_motion_wait_s(
        close_setup_response.commanded_angle_deg,
        CLOSE_ENDPOINT_DEG,
    )
    time.sleep(close_wait_s)

    close_stop_response = client.send_command(
        "STOP",
        case_id="V10-OPEN",
    )

    if not isinstance(close_stop_response, AckMessage):
        return ValidationResult(
            case_id="V10-OPEN",
            case_name="OPEN software endpoint snapshot",
            status="FAIL",
            observed=(
                "CLOSE endpoint STOP did not return "
                "an AckMessage."
            ),
        )

    open_response = client.send_command(
        "OPEN",
        case_id="V10-OPEN",
    )

    if not isinstance(open_response, AckMessage):
        return ValidationResult(
            case_id="V10-OPEN",
            case_name="OPEN software endpoint snapshot",
            status="FAIL",
            observed=(
                "OPEN command did not return "
                "an AckMessage."
            ),
        )

    open_wait_s = calculate_motion_wait_s(
        open_response.commanded_angle_deg,
        OPEN_ENDPOINT_DEG,
    )
    time.sleep(open_wait_s)

    endpoint_response = client.send_command(
        "OPEN",
        case_id="V10-OPEN",
    )

    if not isinstance(endpoint_response, AckMessage):
        return ValidationResult(
            case_id="V10-OPEN",
            case_name="OPEN software endpoint snapshot",
            status="FAIL",
            observed=(
                "OPEN endpoint snapshot did not return "
                "an AckMessage."
            ),
        )

    checks = [
        close_stop_response.commanded_angle_deg
        == CLOSE_ENDPOINT_DEG,
        open_response.command == "OPEN",
        open_response.result == "APPLIED",
        open_response.actuator_mode == "OPEN",
        endpoint_response.command == "OPEN",
        endpoint_response.result == "DUPLICATE",
        endpoint_response.actuator_mode == "OPEN",
        endpoint_response.commanded_angle_deg
        == OPEN_ENDPOINT_DEG,
    ]

    status = "PASS" if all(checks) else "FAIL"

    observed = (
        f"setup_angle="
        f"{close_stop_response.commanded_angle_deg}; "
        f"open_start_angle="
        f"{open_response.commanded_angle_deg}; "
        f"open_wait_s={open_wait_s:.2f}; "
        f"endpoint_result={endpoint_response.result}; "
        f"endpoint_angle="
        f"{endpoint_response.commanded_angle_deg}"
    )

    return ValidationResult(
        case_id="V10-OPEN",
        case_name="OPEN software endpoint snapshot",
        status=status,
        observed=observed,
    )


def run_close_endpoint_case(
    client: SerialClient,
) -> ValidationResult:
    stop_setup_response = client.send_command(
        "STOP",
        case_id="V10-CLOSE",
    )

    if not isinstance(stop_setup_response, AckMessage):
        return ValidationResult(
            case_id="V10-CLOSE",
            case_name="CLOSE software endpoint snapshot",
            status="FAIL",
            observed=(
                "STOP setup command did not return "
                "an AckMessage."
            ),
        )

    close_response = client.send_command(
        "CLOSE",
        case_id="V10-CLOSE",
    )

    if not isinstance(close_response, AckMessage):
        return ValidationResult(
            case_id="V10-CLOSE",
            case_name="CLOSE software endpoint snapshot",
            status="FAIL",
            observed=(
                "CLOSE command did not return "
                "an AckMessage."
            ),
        )

    close_wait_s = calculate_motion_wait_s(
        close_response.commanded_angle_deg,
        CLOSE_ENDPOINT_DEG,
    )
    time.sleep(close_wait_s)

    endpoint_response = client.send_command(
        "CLOSE",
        case_id="V10-CLOSE",
    )

    if not isinstance(endpoint_response, AckMessage):
        return ValidationResult(
            case_id="V10-CLOSE",
            case_name="CLOSE software endpoint snapshot",
            status="FAIL",
            observed=(
                "CLOSE endpoint snapshot did not return "
                "an AckMessage."
            ),
        )

    checks = [
        stop_setup_response.command == "STOP",
        stop_setup_response.result == "APPLIED",
        stop_setup_response.actuator_mode == "STOP",
        close_response.command == "CLOSE",
        close_response.result == "APPLIED",
        close_response.actuator_mode == "CLOSE",
        endpoint_response.command == "CLOSE",
        endpoint_response.result == "DUPLICATE",
        endpoint_response.actuator_mode == "CLOSE",
        endpoint_response.commanded_angle_deg
        == CLOSE_ENDPOINT_DEG,
    ]

    status = "PASS" if all(checks) else "FAIL"

    observed = (
        f"setup_angle="
        f"{stop_setup_response.commanded_angle_deg}; "
        f"close_start_angle="
        f"{close_response.commanded_angle_deg}; "
        f"close_wait_s={close_wait_s:.2f}; "
        f"endpoint_result={endpoint_response.result}; "
        f"endpoint_angle="
        f"{endpoint_response.commanded_angle_deg}"
    )

    return ValidationResult(
        case_id="V10-CLOSE",
        case_name="CLOSE software endpoint snapshot",
        status=status,
        observed=observed,
    )


def main() -> None:
    print(f"Opening {PORT} at {BAUD_RATE} baud...")

    client = SerialClient(
        port=PORT,
        baud_rate=BAUD_RATE,
        response_timeout_s=RESPONSE_TIMEOUT_S,
        read_timeout_s=0.1,
    )

    try:
        client.open()

        ready_message = client.wait_ready(
            timeout_s=READY_TIMEOUT_S,
            case_id="V02",
        )

        print(
            "READY received: "
            f"version={ready_message.protocol_version}, "
            f"mode={ready_message.actuator_mode}, "
            f"angle={ready_message.commanded_angle_deg}"
        )

        print(
            f"Recorded {len(client.events)} "
            "serial event(s)."
        )

        validation_results: list[ValidationResult] = []

        ready_result = validate_ready_message(
            ready_message,
        )
        validation_results.append(ready_result)

        print(
            f"{ready_result.case_id} "
            f"{ready_result.status}: "
            f"{ready_result.observed}"
        )

        invalid_result = run_invalid_command_case(
            client,
            ready_message,
        )
        validation_results.append(invalid_result)

        print(
            f"{invalid_result.case_id} "
            f"{invalid_result.status}: "
            f"{invalid_result.observed}"
        )

        stop_freeze_result = run_stop_freeze_case(
            client,
        )
        validation_results.append(stop_freeze_result)

        print(
            f"{stop_freeze_result.case_id} "
            f"{stop_freeze_result.status}: "
            f"{stop_freeze_result.observed}"
        )

        direction_reversal_result = (
            run_direction_reversal_case(
                client,
            )
        )
        validation_results.append(
            direction_reversal_result
        )

        print(
            f"{direction_reversal_result.case_id} "
            f"{direction_reversal_result.status}: "
            f"{direction_reversal_result.observed}"
        )

        open_endpoint_result = run_open_endpoint_case(
            client,
        )
        validation_results.append(open_endpoint_result)

        print(
            f"{open_endpoint_result.case_id} "
            f"{open_endpoint_result.status}: "
            f"{open_endpoint_result.observed}"
        )

        close_endpoint_result = (
            run_close_endpoint_case(
                client,
            )
        )
        validation_results.append(
            close_endpoint_result
        )

        print(
            f"{close_endpoint_result.case_id} "
            f"{close_endpoint_result.status}: "
            f"{close_endpoint_result.observed}"
        )

        print(
            f"Collected {len(validation_results)} "
            "validation results."
        )

        save_validation_summary(validation_results)

        print(
            "Saved validation summary: "
            f"{VALIDATION_SUMMARY_PATH}"
        )

        save_serial_events(client.events)

        print(
            "Saved serial event log: "
            f"{SERIAL_EVENT_LOG_PATH}"
        )

        print(
            f"Collected {len(client.events)} "
            "serial events."
        )

    finally:
        client.close()
        print("Serial port closed.")
        
if __name__ == "__main__":
    main()