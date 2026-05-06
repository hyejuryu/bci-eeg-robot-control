#전체 코드 흐름
#1. subject 1의 run 1, run 2 EDF 파일 위치를 찾는다
#2. EDF 파일을 MNE로 연다. 
#3. 샘플링 주파수, 채널 수, 샘플 수, 시간 길이, annotation을 확인한다. 
#4. 실제 EEG 데이터 배열의 shape를 확인한다. 
#5. 결과를 results/session-06 폴더에 JSON으로 저장한다.

#목표: EEG 데이터가 Python 안에서 어떤 구조로 들어오는지 이해한다. 

from pathlib import Path
import json

#그래프 그리기
import matplotlib.pyplot as plt

#MNE 안에 들어 있는 PhysioNet EEGBCI 데이터셋 다운로드/불러오기
import mne
from mne.datasets import eegbci

#결과 저장 폴더 정하기
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "session-06"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

#figure 저장 폴더
FIGURE_DIR = PROJECT_ROOT / "figures" / "session-06"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

#1번 참가자 데이터의 run 1(eyes open baseline)과 run 2(eyes closed baseline)
SUBJECT = 1
RUNS = [1, 2]

#run 번호에 이름 붙이기
RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

#run 하나를 열어서 구조 확인
#화면에 제목 출력
def inspect_run(run):
    print(f"\n=== Run {run}: {RUN_LABELS[run]} ===")

    file_path = eegbci.load_data(SUBJECT, [run])[0] #데이터 파일 위치 가져오기

    #EDF 파일을 Raw 객체로 읽음
    #데이터를 메모리에 바로 올림
    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False) 

    sfreq = raw.info["sfreq"] #sampling frequency 확인
    n_channels = len(raw.ch_names) #채널 수 확인
    n_samples = raw.n_times #샘플 수 확인 
    duration_sec = raw.times[-1] #마지막 time point의 시간 값
    data = raw.get_data() #실제 EEG 숫자 꺼내기. shape은 보통 channels x samples

    summary = {
        "subject": SUBJECT,
        "run": run,
        "condition": RUN_LABELS[run],
        "file_path": str(file_path),
        "sampling_frequency_hz": float(sfreq),
        "n_channels": int(n_channels),
        "n_samples": int(n_samples),
        "duration_seconds": float(duration_sec),
        "data_shape_channels_x_samples": list(data.shape), #EEG 배열 구조: 채널 수 x 샘플 수
        "first_10_channel_names": raw.ch_names[:10], #앞에서부터 10개 채널 이름만 미리보기
        "all_channel_names": raw.ch_names, #전체 채널 이름
        "annotations": [
            {
                "onset": float(a["onset"]), #시작 시간
                "duration": float(a["duration"]), #지속 시간 
                "description": str(a["description"]), #설명
            }
            for a in raw.annotations
        ],
        "data_min_volts": float(data.min()),
        "data_max_volts": float(data.max()),
        "note": "MNE stores EEG data in volts. EEG plots are often shown in microvolts.", #단위 메모
    }

    output_path = RESULT_DIR / f"subject-001_run-{run:02d}_{RUN_LABELS[run]}_raw_summary.json"

    #summary 내용을 JSON 파일로 저장 
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    #화면에 요약 출력
    print("file:", file_path)
    print("sampling frequency:", sfreq)
    print("channels:", n_channels)
    print("samples:", n_samples)
    print("duration:", duration_sec)
    print("data shape:", data.shape)
    print("first 10 channels:", raw.ch_names[:10])
    print("saved:", output_path)

    #61초 중 첫 10초 EEG waveform 시각화
    start_sec = 0
    stop_sec = 10

    #시간을 sample index로 변환 
    #1 sec = 160 samples
    start_sample = int(start_sec * sfreq) #0
    stop_sample = int(stop_sec * sfreq) #1600

    #EEG 채널만 선택
    #ECG(심전도), EMG(근전도) 등등 데이터 제외
    #뭘 분석 중인지 명시하는 코드
    picks = mne.pick_types(raw.info, eeg=True, exclude=[ ])

    #64개 채널 중 subset으로 앞의 8개 채널만 선택
    selected_picks = picks[:8]

    #선택한 구간 데이터 가져오기
    #8개 채널 x 1600 samples
    data_segment, times = raw[selected_picks, start_sample:stop_sample]

    #volts → microvolts 변환
    data_segment_uv = data_segment * 1e6

    plt.figure(figsize=(12, 6))

    #채널 waveform이 서로 겹치지 않도록 세로 간격 추가
    offset = 100

    for idx, channel_data in enumerate(data_segment_uv):
        channel_name = raw.ch_names[selected_picks[idx]]

        plt.plot(
            times,
            channel_data + idx * offset,
            label=channel_name
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude + offset (uV)")
    plt.title(f"Run {run}: {RUN_LABELS[run]} - First 10 seconds")

    plt.legend(loc="upper right", fontsize=8)

    plt.tight_layout()

    fig_path = (
        FIGURE_DIR
        / f"subject-001_run-{run:02d}_{RUN_LABELS[run]}_first_10s.png"
    )

    plt.savefig(fig_path, dpi=150)

    plt.close()

    print("saved figure:", fig_path)

if __name__ == "__main__":
    for run in RUNS:
        inspect_run(run)

    print("\nSession 06 raw inspection completed.")