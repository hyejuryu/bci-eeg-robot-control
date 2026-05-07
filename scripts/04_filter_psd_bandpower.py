#코드 목적
#7회차 주파수 분석을 위해 EEG 데이터와 후두부 채널이 제대로 준비됐는지 확인 

from pathlib import Path

import mne
from mne.datasets import eegbci

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULT_DIR = PROJECT_ROOT / "results" / "session-07"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

FIGURE_DIR = PROJECT_ROOT / "figures" / "session-07"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

#1번 참가자의 run 1과 run 2 분석
SUBJECT = 1
RUNS = [1, 2]

#딕셔너리
RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

#분석할 채널 정하기
#eyes closed alpha 확인 위해 posterior 영역 채널
POSTERIOR_CHANNELS = [
    "Po3.",
    "Poz.",
    "Po4.",
    "O1..",
    "Oz..",
    "O2..",
]


#데이터를 여는 함수 
#run 번호를 입력 받아 해당 EDF 파일을 MNE Raw 객체로 불러오는 함수
#run 번호를 넣고, 해당 EDF 파일 찾아서 MNE Raw 객체로 열고 raw를 돌려줌
def load_raw(run):
    file_path = eegbci.load_data(SUBJECT, [run])[0]
    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
    return raw


#실제 실행 부분 
#분석하려는 posterior 채널들이 실제 데이터 안에 있는지 확인 
if __name__ == "__main__":
    for run in RUNS:
        raw = load_raw(run)
        raw_filtered = raw.copy().filter(l_freq=1, h_freq=40, verbose=False) #raw 원본은 그대로 두고 복사본을 만든 다음 1~40Hz만 남김
        raw_posterior = raw_filtered.copy().pick(POSTERIOR_CHANNELS) #필터링된 데이터 중 후두부 채널 6개만 남긴 데이터
        psd = raw_posterior.compute_psd(method="welch", fmin=1, fmax=40, verbose=False) #주파수별 power 계산 #Welch 방식으로 PSD 계산 #1~40Hz 범위만 계산


        print("\n====================")
        print("Run:", run, RUN_LABELS[run])
        print("Sampling frequency:", raw.info["sfreq"])
        print("Number of channels:", len(raw.ch_names))
        print("Filtering completed: 1~40Hz")
        print("Posterior channels found:")

        for ch in POSTERIOR_CHANNELS:
            print(ch, ch in raw.ch_names)

        print("PSD computed using Welch method")
        print("PSD shape:", psd.get_data().shape)