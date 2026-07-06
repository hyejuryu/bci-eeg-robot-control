"""
Session 12 - BrainFlow posterior contact-assisted Cyton acquisition check.

This script verifies short OpenBCI Cyton acquisition, raw file saving,
metadata logging, and readback verification after OpenBCI GUI contact sanity
check supports posterior contact-assisted recording.

The intended setup uses Ten20 conductive paste / gel and OpenBCI gold cup
electrodes for approximate posterior contact-assisted acquisition.

No EEG feature interpretation, alpha validation, focus estimation, or robot
control is performed.
"""

import argparse
import json
import time
import subprocess  # for serial_port_preflight
from datetime import datetime
from pathlib import Path
import importlib.metadata as package_metadata

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter


def run_serial_port_preflight(requested_port):
    """Soft preflight check for available Windows serial ports."""

    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "[System.IO.Ports.SerialPort]::GetPortNames()",
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        return {
            "requested_serial_port": requested_port,
            "method": "PowerShell System.IO.Ports.SerialPort.GetPortNames",
            "check_performed": False,
            "available_ports": [],
            "requested_port_found": None,
            "status": "skipped",
            "reason": f"port listing command failed: {exc}",
        }

    if completed.returncode != 0:
        return {
            "requested_serial_port": requested_port,
            "method": "PowerShell System.IO.Ports.SerialPort.GetPortNames",
            "check_performed": False,
            "available_ports": [],
            "requested_port_found": None,
            "status": "skipped",
            "reason": completed.stderr.strip()
            or "port listing command returned non-zero exit code",
        }

    available_ports = [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.strip()
    ]

    requested_port_found = requested_port.upper() in {
        port.upper() for port in available_ports
    }

    return {
        "requested_serial_port": requested_port,
        "method": "PowerShell System.IO.Ports.SerialPort.GetPortNames",
        "check_performed": True,
        "available_ports": available_ports,
        "requested_port_found": requested_port_found,
        "status": "passed" if requested_port_found else "failed",
    }


def print_pre_run_checklist():
    """Print manual hardware/setup checklist without starting a recording."""

    print("\nSession 12 - posterior contact-assisted Cyton pre-run checklist\n")

    checklist = [
        "OpenBCI GUI contact sanity check has been completed first.",
        "OpenBCI GUI is closed before BrainFlow recording.",
        "Cyton is battery powered.",
        "Cyton board switch is set to PC.",
        "USB dongle switch is set to GPIO6 side.",
        "USB dongle is connected.",
        "COM3 is expected unless a different serial port is provided.",
        "Arduino / robot hardware is disconnected.",
        "Posterior contact-assisted setup is documented in the Session 12 log.",
    ]

    for item in checklist:
        print(f"[ ] {item}")

    print(
        """

Montage / setup to use:
[ ] Ch1 / N1P: approximate posterior candidate
[ ] gold cup electrode
[ ] Ten20 conductive paste / gel
[ ] SRB / SRB2: left earclip unless changed and documented
[ ] BIAS: right earclip unless changed and documented
[ ] Ch2 / N2P optional only if documented
[ ] Ch3-Ch8 off or ignored

Scope:
Posterior contact-assisted acquisition check after GUI contact sanity check.
No EEG feature interpretation, alpha validation, focus estimation, or robot control is performed.
"""
    )


def main():
    # ---------------------------------------------------------------------
    # 1. Command-line options
    # ---------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Session 12 posterior contact-assisted OpenBCI Cyton BrainFlow acquisition check."
    )

    parser.add_argument(
        "--serial-port",
        default="COM3",
        help="Serial port for OpenBCI Cyton dongle. Default: COM3",
    )

    parser.add_argument(
        "--duration-sec",
        type=float,
        default=5.0,
        help="Short recording duration in seconds. Default: 5.0",
    )

    parser.add_argument(
        "--print-checklist",
        action="store_true",
        help="Print the pre-run checklist and exit without connecting to Cyton.",
    )

    parser.add_argument(
        "--confirm-prerun",
        action="store_true",
        help="Required before actual Cyton recording starts.",
    )

    parser.add_argument(
        "--confirm-gui-contact-check",
        action="store_true",
        help="Required after GUI contact sanity check supports BrainFlow recording.",
    )

    parser.add_argument(
        "--include-ch2",
        action="store_true",
        help="Record Ch2 / N2p as included in the documented posterior setup.",
    )

    args = parser.parse_args()

    if args.print_checklist:
        print_pre_run_checklist()
        return

    if not args.confirm_prerun:
        print("\nNo recording started.")
        print("Reason: --confirm-prerun was not provided.")
        print_pre_run_checklist()
        print("After checking the setup manually, run again with --confirm-prerun.\n")
        return

    if not args.confirm_gui_contact_check:
        print("\nNo recording started.")
        print("Reason: --confirm-gui-contact-check was not provided.")
        print("Run BrainFlow only after GUI contact sanity check supports short recording.\n")
        print_pre_run_checklist()
        return

    if args.duration_sec <= 0:
        raise ValueError("--duration-sec must be greater than 0.")

    # ---------------------------------------------------------------------
    # 2. Basic session settings
    # ---------------------------------------------------------------------
    session_id = "session-12"
    test_label = "brainflow-cyton-posterior-contact-assisted"
    purpose = "Posterior contact-assisted Cyton acquisition check after GUI contact sanity check"
    requested_duration_sec = args.duration_sec

    # This script is located in scripts/.
    # parents[1] means: scripts/.. = project root.
    project_root = Path(__file__).resolve().parents[1]

    raw_dir = project_root / "data" / "raw" / "session-12"
    results_dir = project_root / "results" / "session-12"

    raw_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp_label = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    raw_file = raw_dir / f"{timestamp_label}_s12_{test_label}_raw.csv"
    metadata_file = raw_dir / f"{timestamp_label}_s12_{test_label}_metadata.json"
    summary_file = results_dir / f"{timestamp_label}_s12_{test_label}_readback_summary.json"

    # ---------------------------------------------------------------------
    # 3. BrainFlow Cyton board setup
    # ---------------------------------------------------------------------
    board_id = BoardIds.CYTON_BOARD.value

    params = BrainFlowInputParams()
    params.serial_port = args.serial_port

    serial_port_preflight = run_serial_port_preflight(args.serial_port)

    print("\nSerial port preflight:")
    print(f"Requested port: {args.serial_port}")
    print(f"Status: {serial_port_preflight['status']}")
    print(f"Available ports: {serial_port_preflight['available_ports']}")

    if serial_port_preflight["status"] == "failed":
        print("\nNo recording started.")
        print(f"Reason: requested serial port was not found: {args.serial_port}")
        print("Check USB dongle connection, Cyton power/switch state, and COM port assignment.\n")
        return

    if serial_port_preflight["status"] == "skipped":
        print("\nSerial port preflight was skipped.")
        print("The script will continue, but BrainFlow may fail if the port is unavailable or occupied.\n")

    # Board metadata and data layout information
    # BrainFlow data is organized as rows x samples (2D array).
    brainflow_version = package_metadata.version("brainflow")
    device_name = BoardShim.get_device_name(board_id)
    sampling_rate = BoardShim.get_sampling_rate(board_id)
    num_rows = BoardShim.get_num_rows(board_id)
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    timestamp_channel = BoardShim.get_timestamp_channel(board_id)

    board = BoardShim(board_id, params)

    data = None
    session_prepared = False
    stream_started = False

    # ---------------------------------------------------------------------
    # 4. Stream actual Cyton data
    # ---------------------------------------------------------------------
    try:
        print("Preparing BrainFlow Cyton session...")
        board.prepare_session()
        session_prepared = True

        print("Starting stream...")
        board.start_stream()
        stream_started = True

        print(f"Collecting Cyton data for {requested_duration_sec} seconds...")
        time.sleep(requested_duration_sec)

        print("Reading data from BrainFlow buffer...")
        data = board.get_board_data()

    finally:
        if stream_started:
            print("Stopping stream...")
            board.stop_stream()

        if session_prepared:
            print("Releasing BrainFlow session...")
            board.release_session()

    # ---------------------------------------------------------------------
    # 5. Save raw Cyton data and local metadata
    # ---------------------------------------------------------------------
    if data is None:
        raise RuntimeError("No data was collected from the Cyton board.")

    print(f"Saving raw Cyton data to: {raw_file}")
    DataFilter.write_file(data, str(raw_file), "w")

    metadata_record = {
        "session_id": session_id,
        "test_label": test_label,
        "purpose": purpose,
        "scope": "Posterior contact-assisted acquisition check after GUI contact sanity check.",
        "created_at_local": timestamp_label,
        "hardware": {
            "board": "OpenBCI Cyton",
            "board_id_name": "CYTON_BOARD",
            "board_id": board_id,
            "device_name": device_name,
            "serial_port": args.serial_port,
            "serial_port_preflight": serial_port_preflight,
            "os": "Windows 11",
            "cyton_power": "LiPo battery",
            "cyton_board_switch": "PC",
            "usb_dongle_switch": "GPIO6 side",
            "openbci_gui_running": False,
            "arduino_robot_hardware_connected": False,
        },
        "montage": {
            "purpose": "Posterior contact-assisted acquisition check",
            "gui_contact_check": "completed before BrainFlow run",
            "ch1": {
                "cyton_input": "N1P",
                "electrode": "OpenBCI gold cup electrode",
                "contact_method": "Ten20 conductive paste / gel",
                "contact_position": "approximate posterior candidate",
            },
            "ch2": {
                "cyton_input": "N2P",
                "included_in_this_recording": args.include_ch2,
                "electrode": "OpenBCI gold cup electrode" if args.include_ch2 else None,
                "contact_method": "Ten20 conductive paste / gel" if args.include_ch2 else None,
                "contact_position": (
                    "optional approximate posterior candidate"
                    if args.include_ch2
                    else None
                ),
                "status": (
                    "included and documented"
                    if args.include_ch2
                    else "not included; optional channel reserved for later use"
                ),
            },
            "srb": {
                "position": "left earclip unless changed and documented",
            },
            "bias": {
                "position": "right earclip unless changed and documented",
            },
            "ch3_to_ch8": "off or ignored",
        },
        "software": {
            "brainflow_version": brainflow_version,
            "python_environment": "bci-eeg",
        },
        "recording": {
            "requested_duration_sec": requested_duration_sec,
            "sampling_rate_hz": sampling_rate,
        },
        "brainflow_layout": {
            "num_rows": num_rows,
            "eeg_channels": eeg_channels,
            "timestamp_channel": timestamp_channel,
            "data_layout": "rows x samples",
        },
        "files": {
            "raw_file": str(raw_file.relative_to(project_root)),
            "metadata_file": str(metadata_file.relative_to(project_root)),
            "summary_file": str(summary_file.relative_to(project_root)),
        },
        "notes": [
            "Actual Cyton hardware was used.",
            "Posterior contact-assisted setup was checked in OpenBCI GUI before BrainFlow recording.",
            "Gold cup electrode and Ten20 conductive paste / gel were used as the documented contact-assisted condition.",
            "This run does not validate alpha reactivity.",
            "This run does not perform PSD, band-power analysis, focus estimation, or robot control.",
        ],
    }

    print(f"Saving local metadata to: {metadata_file}")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata_record, f, indent=2)

    # ---------------------------------------------------------------------
    # 6. Read back saved file
    # ---------------------------------------------------------------------
    print("Reading saved file back...")
    restored_data = DataFilter.read_file(str(raw_file))

    original_shape = list(data.shape)
    restored_shape = list(restored_data.shape)

    sample_count = int(data.shape[1])
    estimated_duration_sec = sample_count / sampling_rate
    expected_sample_count = requested_duration_sec * sampling_rate

    shape_match = original_shape == restored_shape
    raw_file_exists = raw_file.exists()
    metadata_file_exists = metadata_file.exists()

    # A loose check is enough here because this is a timing-based stream test.
    sample_count_plausible = (
        sample_count > 0
        and abs(sample_count - expected_sample_count) < sampling_rate
    )

    # ---------------------------------------------------------------------
    # 7. Save readback summary
    # ---------------------------------------------------------------------
    summary = {
        "session_id": session_id,
        "test_label": test_label,
        "purpose": purpose,
        "hardware_used": "OpenBCI Cyton",
        "board": {
            "board_id": board_id,
            "board_id_name": "CYTON_BOARD",
            "device_name": device_name,
            "brainflow_version": brainflow_version,
            "sampling_rate_hz": sampling_rate,
            "num_rows": num_rows,
            "eeg_channels": eeg_channels,
            "timestamp_channel": timestamp_channel,
        },
        "recording": {
            "requested_duration_sec": requested_duration_sec,
            "expected_sample_count": expected_sample_count,
            "actual_sample_count": sample_count,
            "estimated_duration_sec": estimated_duration_sec,
            "sample_count_plausibility_criterion": "abs(actual_sample_count - expected_sample_count) < sampling_rate_hz",
        },
        "montage_summary": {
            "active_channels": ["Ch1 / N1P"]
            + (["Ch2 / N2P"] if args.include_ch2 else []),
            "contact_method": "posterior gold cup electrode + Ten20 conductive paste / gel",
            "reference": "SRB / SRB2 left earclip unless changed and documented",
            "bias": "right earclip unless changed and documented",
            "gui_contact_check": "completed before BrainFlow run",
        },
        "files": {
            "raw_file": str(raw_file.relative_to(project_root)),
            "metadata_file": str(metadata_file.relative_to(project_root)),
            "summary_file": str(summary_file.relative_to(project_root)),
            "raw_file_exists": raw_file_exists,
            "metadata_file_exists": metadata_file_exists,
            "raw_signal_values_included_in_summary": False,
        },
        "readback": {
            "readback_succeeded": True,
            "original_shape": original_shape,
            "restored_shape": restored_shape,
            "shape_match": shape_match,
            "sample_count_plausible": sample_count_plausible,
        },
        "scope_boundary": {
            "supports": [
                "short BrainFlow Cyton acquisition after GUI contact sanity check",
                "raw file saving and local metadata logging",
                "readback, shape, and sample-count plausibility checks",
            ],
            "does_not_support": [
                "EEG feature interpretation",
                "posterior alpha validation",
                "focus or attention estimation",
                "robot control readiness",
            ],
        },
        "notes": [
            "Readback summary does not include raw signal values.",
            "Actual raw CSV and metadata JSON are local-only under data/raw/session-12/.",
        ],
    }

    print(f"Saving readback summary to: {summary_file}")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # ---------------------------------------------------------------------
    # 8. Console summary
    # ---------------------------------------------------------------------
    print("\nSession 12 posterior Cyton save/readback test complete.")
    print(f"BrainFlow version: {brainflow_version}")
    print(f"Device name: {device_name}")
    print(f"Serial port: {args.serial_port}")
    print(f"Sampling rate: {sampling_rate} Hz")
    print(f"Original shape: {original_shape}")
    print(f"Restored shape: {restored_shape}")
    print(f"Shape match: {shape_match}")
    print(f"Sample count plausible: {sample_count_plausible}")
    print(f"Raw file: {raw_file.relative_to(project_root)}")
    print(f"Metadata file: {metadata_file.relative_to(project_root)}")
    print(f"Summary file: {summary_file.relative_to(project_root)}")

    if not shape_match or not sample_count_plausible:
        print("\nThe file was created, but readback/sample-count verification needs review.")


if __name__ == "__main__":
    main()