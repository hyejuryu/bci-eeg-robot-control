"""
Session 11 - BrainFlow Cyton acquisition pipeline check.

This script verifies actual OpenBCI Cyton acquisition, raw file saving,
metadata logging, and readback verification using a known-good Ch1 forehead montage.

No EEG feature interpretation or robot control is performed.
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
import importlib.metadata as package_metadata

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter


def print_pre_run_checklist():
    """Print manual hardware/setup checklist without starting a recording."""

    print("\nSession 11 - Cyton pre-run checklist\n")

    checklist = [
        "OpenBCI GUI is closed.",
        "Cyton is battery powered.",
        "Cyton board switch is set to PC.",
        "USB dongle switch is set to GPIO6 side.",
        "USB dongle is connected.",
        "COM3 is expected.",
        "Arduino / robot hardware is disconnected.",
        "Known-good Ch1 forehead flat A montage is prepared.",
    ]

    for item in checklist:
        print(f"[ ] {item}")

    print(
        """

Montage to use:
[ ] Ch1 / N1P
[ ] black snap cable
[ ] flat electrode A
[ ] forehead contact
[ ] SRB earclip unchanged
[ ] BIAS earclip unchanged
[ ] Ch2-Ch8 off or ignored

Scope:
Acquisition infrastructure verification only.
No EEG feature interpretation or robot control is performed.
"""
    )


def main():
    # ---------------------------------------------------------------------
    # 1. Command-line options
    # ---------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Session 11 actual OpenBCI Cyton BrainFlow acquisition check."
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

    if args.duration_sec <= 0:
        raise ValueError("--duration-sec must be greater than 0.")

    # ---------------------------------------------------------------------
    # 2. Basic session settings
    # ---------------------------------------------------------------------
    session_id = "session-11"
    test_label = "brainflow-cyton-ch1-forehead"
    purpose = "OpenBCI Cyton acquisition pipeline verification"
    requested_duration_sec = args.duration_sec

    # This script is located in scripts/.
    # parents[1] means: scripts/.. = project root.
    project_root = Path(__file__).resolve().parents[1]

    raw_dir = project_root / "data" / "raw" / "session-11"
    results_dir = project_root / "results" / "session-11"

    raw_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp_label = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    raw_file = raw_dir / f"{timestamp_label}_s11_{test_label}_raw.csv"
    metadata_file = raw_dir / f"{timestamp_label}_s11_{test_label}_metadata.json"
    summary_file = results_dir / f"{timestamp_label}_s11_{test_label}_readback_summary.json"

    # ---------------------------------------------------------------------
    # 3. BrainFlow Cyton board setup
    # ---------------------------------------------------------------------
    board_id = BoardIds.CYTON_BOARD.value

    params = BrainFlowInputParams()
    params.serial_port = args.serial_port

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
        "scope": "Acquisition infrastructure verification only.",
        "created_at_local": timestamp_label,
        "hardware": {
            "board": "OpenBCI Cyton",
            "board_id_name": "CYTON_BOARD",
            "board_id": board_id,
            "device_name": device_name,
            "serial_port": args.serial_port,
            "os": "Windows 11",
            "cyton_power": "LiPo battery",
            "cyton_board_switch": "PC",
            "usb_dongle_switch": "GPIO6 side",
            "openbci_gui_running": False,
            "arduino_robot_hardware_connected": False,
        },
        "montage": {
            "purpose": "Known-good acquisition pipeline sanity check",
            "ch1": {
                "cyton_input": "N1P",
                "snap_cable": "black",
                "electrode": "flat electrode A",
                "contact_position": "forehead",
            },
            "srb": {
                "position": "earclip unchanged from Session 10",
            },
            "bias": {
                "position": "earclip unchanged from Session 10",
            },
            "ch2_to_ch8": "off or ignored",
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
            "Known-good Ch1 forehead flat-electrode montage was used.",
            "This run does not validate posterior alpha reactivity.",
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
                "BrainFlow Cyton acquisition pipeline verification",
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
            "Actual raw CSV and metadata JSON are local-only under data/raw/session-11/.",
        ],
    }

    print(f"Saving readback summary to: {summary_file}")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # ---------------------------------------------------------------------
    # 8. Console summary
    # ---------------------------------------------------------------------
    print("\nCyton save/readback test complete.")
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