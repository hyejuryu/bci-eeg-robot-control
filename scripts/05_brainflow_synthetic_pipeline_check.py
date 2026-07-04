"""
Session 11 - BrainFlow synthetic board pipeline check.

Purpose:
- Verify the BrainFlow acquisition, raw file saving, readback, and summary generation workflow 
  before connecting to the real OpenBCI cyton board.

This script uses BrainFlow's synthetic board.
No real EEG hardware or human biosignal data is used.
"""

import json
import time
from datetime import datetime
from pathlib import Path
import importlib.metadata as metadata

# Boardshim: BrainFlow board session 제어 / board data 읽기
# BrainFlowInputParams: board 연결에 필요한 설정값을 담는 객체
# BoardIds: 사용할 board 종류를 지정하는 목록
# DataFilter: BrainFlow data 저장/readback 및 signal/data handling 도구

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter


def main():
    # ---------------------------------------------------------------------
    # 1. Basic session settings
    # ---------------------------------------------------------------------
    session_id = "session-11"
    test_label = "brainflow-synthetic"
    requested_duration_sec = 5  # 저장/readback pipeline 작동 확인용 짧은 stream duration

    # This script is located in scripts/.
    # parents[1] means: scripts/.. = project root.
    project_root = Path(__file__).resolve().parents[1]

    output_dir = project_root / "results" / "session-11"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp_label = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    raw_file = output_dir / f"{timestamp_label}_s11_{test_label}_raw.csv"
    summary_file = output_dir / f"{timestamp_label}_s11_{test_label}_readback_summary.json"

    # ---------------------------------------------------------------------
    # 2. BrainFlow board setup
    # ---------------------------------------------------------------------
    board_id = BoardIds.SYNTHETIC_BOARD.value
    params = BrainFlowInputParams()

    # Board metadata and data layout information
    # BrainFlow data is organized as rows x samples (2D array).
    brainflow_version = metadata.version("brainflow")
    device_name = BoardShim.get_device_name(board_id)
    sampling_rate = BoardShim.get_sampling_rate(board_id)
    num_rows = BoardShim.get_num_rows(board_id)
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    timestamp_channel = BoardShim.get_timestamp_channel(board_id)

    board = BoardShim(board_id, params)

    data = None
    stream_started = False

    # ---------------------------------------------------------------------
    # 3. Stream synthetic data
    # ---------------------------------------------------------------------
    # try ... finally ensures that stream/session cleanup runs even if an error occurs.  
    try:
        print("Preparing BrainFlow synthetic board session...")
        board.prepare_session()

        print("Starting stream...")
        board.start_stream()
        stream_started = True

        print(f"Collecting synthetic data for {requested_duration_sec} seconds...")
        time.sleep(requested_duration_sec)

        print("Reading data from BrainFlow buffer...")
        data = board.get_board_data()

    finally:
        if stream_started:
            print("Stopping stream...")
            board.stop_stream()

        print("Releasing BrainFlow session...")
        board.release_session()

    # ---------------------------------------------------------------------
    # 4. Save raw synthetic data
    # ---------------------------------------------------------------------
    if data is None:
        raise RuntimeError("No data was collected from the synthetic board.")

    print(f"Saving raw synthetic data to: {raw_file}")
    DataFilter.write_file(data, str(raw_file), "w")

    # ---------------------------------------------------------------------
    # 5. Read back saved file
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

    # A loose check is enough here because this is a timing-based stream test.
    sample_count_plausible = sample_count > 0 and abs(sample_count - expected_sample_count) < sampling_rate

    # ---------------------------------------------------------------------
    # 6. Save readback summary
    # ---------------------------------------------------------------------
    summary = {
        "session_id": session_id,
        "test_label": test_label,
        "purpose": "BrainFlow synthetic-board acquisition pipeline verification",
        "hardware_used": "none",
        "board": {
            "board_id": board_id,
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
            "summary_file": str(summary_file.relative_to(project_root)),
            "raw_file_exists": raw_file_exists,
        },
        "readback": {
            "readback_succeeded": True,
            "original_shape": original_shape,
            "restored_shape": restored_shape,
            "shape_match": shape_match,
            "sample_count_plausible": sample_count_plausible,
        },
        "notes": [
            "Synthetic board test only.",
            "No real Cyton hardware was used.",
            "No human biosignal data was collected.",
        ],
    }

    print(f"Saving readback summary to: {summary_file}")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # ---------------------------------------------------------------------
    # 7. Console summary
    # ---------------------------------------------------------------------
    print("\nSynthetic board save/readback test complete.")
    print(f"BrainFlow version: {brainflow_version}")
    print(f"Device name: {device_name}")
    print(f"Sampling rate: {sampling_rate} Hz")
    print(f"Original shape: {original_shape}")
    print(f"Restored shape: {restored_shape}")
    print(f"Shape match: {shape_match}")
    print(f"Sample count plausible: {sample_count_plausible}")
    print(f"Raw file: {raw_file.relative_to(project_root)}")
    print(f"Summary file: {summary_file.relative_to(project_root)}")


if __name__ == "__main__":
    main()