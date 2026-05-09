# 코드 목적
# EEGBCI baseline eyes open / eyes closed 데이터를 이용해
# posterior channel의 Welch PSD를 계산하고,
# alpha/beta band power를 비교한 뒤
# PSD figure와 band power CSV를 저장한다.

from pathlib import Path
import csv

import matplotlib.pyplot as plt
import mne
from mne.datasets import eegbci

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULT_DIR = PROJECT_ROOT / "results" / "session-07"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

FIGURE_DIR = PROJECT_ROOT / "figures" / "session-07"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# 1번 참가자의 run 1과 run 2 분석
SUBJECT = 1
RUNS = [1, 2]

# run 번호별 조건 이름
RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

# 출력 옵션
# True: frequency values와 PSD data 전체 출력
# False: 일부 값만 preview로 출력
PRINT_FULL_ARRAYS = False

# preview 모드에서 앞에서 몇 개의 값만 볼지 설정
N_PREVIEW = 10

# 분석할 frequency band 정의
# alpha : 눈 감았을 때 posterior 영역에서 강해지는지 확인할 핵심 band
# beta : 이후 focus/task 조건 분석을 위해 함께 확인할 band
ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)

# 분석할 채널 정하기
# eyes closed alpha 확인을 위해 posterior 영역 채널 선택
POSTERIOR_CHANNELS = [
    "Po3.",
    "Poz.",
    "Po4.",
    "O1..",
    "Oz..",
    "O2..",
]


# 데이터를 여는 함수
# run 번호를 입력받아 해당 EDF 파일을 MNE Raw 객체로 불러옴
def load_raw(run):
    file_path = eegbci.load_data(SUBJECT, [run])[0]
    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
    return raw


# 실제 실행 부분
if __name__ == "__main__":
    posterior_mean_psd_by_run = {}
    freqs_by_run = {}

    # alpha/beta power 계산 결과를 CSV로 저장하기 위해 모아둘 리스트
    band_power_rows = []

    for run in RUNS:
        raw = load_raw(run)

        # raw 원본은 그대로 두고 복사본을 만든 다음 1~40Hz만 남김
        raw_filtered = raw.copy().filter(
            l_freq=1,
            h_freq=40,
            verbose=False
        )

        # 필터링된 데이터 중 posterior 채널 6개만 남김
        raw_posterior = raw_filtered.copy().pick(POSTERIOR_CHANNELS)

        # Welch method를 사용해 PSD 계산
        # fmin=1, fmax=40은 1~40Hz 범위의 주파수 성분만 보겠다는 뜻
        psd = raw_posterior.compute_psd(
            method="welch",
            fmin=1,
            fmax=40,
            verbose=False
        )

        # PSD 객체에서 실제 power 데이터 꺼내기
        # psd_data는 각 채널별, 각 주파수별 power 값을 담고 있음
        psd_data = psd.get_data()

        # PSD의 x축 값인 frequency values를 따로 변수에 저장
        freqs = psd.freqs

        print("\n====================")
        print("Run:", run, RUN_LABELS[run])
        print("Sampling frequency:", raw.info["sfreq"])
        print("Number of channels:", len(raw.ch_names))
        print("Filtering completed: 1~40Hz")
        print("Posterior channels found:")

        for ch in POSTERIOR_CHANNELS:
            print(ch, ch in raw.ch_names)

        print("PSD computed using Welch method")

        # PSD 데이터 형태 확인
        # shape = (채널 수, 주파수 지점 수)
        # 이번 실행 결과 예: (6, 500)
        # 6 = posterior 채널 수
        # 500 = 계산된 주파수 지점 개수
        print("PSD shape:", psd_data.shape)

        # PSD의 주파수 지점 개수 확인
        # 이 값은 psd_data.shape의 두 번째 숫자와 같아야 함
        print("Number of frequency points:", len(freqs))

        print("PSD frequency values:")

        if PRINT_FULL_ARRAYS:
            # 전체 frequency values 출력
            print(freqs)
        else:
            # 앞부분 일부만 출력
            print(f"First {N_PREVIEW} frequency values:")
            print(freqs[:N_PREVIEW])

        # Welch PSD 결과의 주파수 간격 확인
        # 예: 1.0, 1.5, 2.0이면 간격은 0.5Hz
        print("Frequency spacing:")
        print(freqs[1] - freqs[0])

        print("PSD data:")

        if PRINT_FULL_ARRAYS:
            # 전체 PSD data 출력
            print(psd_data)
        else:
            # 첫 번째 posterior 채널의 PSD 값 중 앞부분 일부만 출력
            print("First channel:", raw_posterior.ch_names[0])
            print(f"First {N_PREVIEW} PSD values:")
            print(psd_data[0, :N_PREVIEW])

        # posterior 채널 6개의 PSD를 평균냄
        # psd_data shape = (채널 수, 주파수 지점 수)
        # 이번 경우: (6, 500)
        #
        # axis=0은 채널 축을 따라 평균을 낸다는 뜻
        # 즉, 각 주파수 지점마다 6개 posterior 채널의 power를 평균냄
        #
        # posterior_mean_psd shape = (주파수 지점 수,)
        # 이번 경우: (500,)
        # 즉, posterior 평균 PSD 1줄이 됨
        posterior_mean_psd = psd_data.mean(axis=0)

        # alpha/beta frequency band에 해당하는 위치 선택
        # alpha: 8Hz 이상, 13Hz 미만
        # beta: 13Hz 이상, 30Hz 이하
        #
        # alpha_mask와 beta_mask는 True/False 배열
        # freqs 중 해당 band에 속하는 주파수 위치만 True가 됨
        alpha_mask = (freqs >= ALPHA_BAND[0]) & (freqs < ALPHA_BAND[1])
        beta_mask = (freqs >= BETA_BAND[0]) & (freqs <= BETA_BAND[1])

        # posterior 평균 PSD에서 alpha/beta 구간만 선택한 뒤 평균 power 계산
        alpha_power = posterior_mean_psd[alpha_mask].mean()
        beta_power = posterior_mean_psd[beta_mask].mean()

        # beta power를 alpha power로 나눈 값
        beta_alpha_ratio = beta_power / alpha_power

        print("Alpha power:", alpha_power)
        print("Beta power:", beta_power)
        print("Beta/Alpha ratio:", beta_alpha_ratio)

        # 현재 run의 band power 결과를 저장용 리스트에 추가
        band_power_rows.append({
            "subject": SUBJECT,
            "run": run,
            "condition": RUN_LABELS[run],
            "n_posterior_channels": len(raw_posterior.ch_names),
            "posterior_channels": ";".join(raw_posterior.ch_names),
            "n_frequency_points": len(freqs),
            "frequency_spacing_hz": float(freqs[1] - freqs[0]),
            "alpha_band_hz": f"{ALPHA_BAND[0]} <= f < {ALPHA_BAND[1]}",
            "beta_band_hz": f"{BETA_BAND[0]} <= f <= {BETA_BAND[1]}",
            "alpha_power": float(alpha_power),
            "beta_power": float(beta_power),
            "beta_alpha_ratio": float(beta_alpha_ratio),
        })

        # 나중에 eyes open / eyes closed를 한 그래프에서 비교하기 위해 저장
        posterior_mean_psd_by_run[run] = posterior_mean_psd
        freqs_by_run[run] = freqs

        # 개별 PSD figure 생성
        plt.figure(figsize=(10, 6))

        # x축 = frequency, y축 = posterior 평균 PSD
        plt.plot(freqs, posterior_mean_psd)

        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power Spectral Density")
        plt.title(f"Posterior Mean PSD - {RUN_LABELS[run]}")

        plt.tight_layout()

        fig_path = (
            FIGURE_DIR
            / f"subject-001_run-{run:02d}_{RUN_LABELS[run]}_posterior_mean_psd.png"
        )

        plt.savefig(fig_path, dpi=150)
        plt.close()

        print("Saved PSD figure:", fig_path)

    # alpha/beta band power 결과를 CSV 파일로 저장
    band_power_csv_path = (
        RESULT_DIR
        / "subject-001_alpha_beta_bandpower_summary.csv"
    )

    with open(band_power_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "subject",
            "run",
            "condition",
            "n_posterior_channels",
            "posterior_channels",
            "n_frequency_points",
            "frequency_spacing_hz",
            "alpha_band_hz",
            "beta_band_hz",
            "alpha_power",
            "beta_power",
            "beta_alpha_ratio",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(band_power_rows)

    print("Saved band power CSV:", band_power_csv_path)

    # Run 1 eyes open과 Run 2 eyes closed의 band power 비교 요약
    run1_row = next(row for row in band_power_rows if row["run"] == 1)
    run2_row = next(row for row in band_power_rows if row["run"] == 2)

    alpha_power_closed_over_open = (
        run2_row["alpha_power"] / run1_row["alpha_power"]
    )

    beta_power_closed_over_open = (
        run2_row["beta_power"] / run1_row["beta_power"]
    )

    beta_alpha_ratio_closed_over_open = (
        run2_row["beta_alpha_ratio"] / run1_row["beta_alpha_ratio"]
    )

    beta_alpha_ratio_open_over_closed = (
        run1_row["beta_alpha_ratio"] / run2_row["beta_alpha_ratio"]
    )

    comparison_rows = [
        {
            "subject": SUBJECT,
            "comparison": "eyes_closed_over_eyes_open",
            "alpha_power_ratio": alpha_power_closed_over_open,
            "beta_power_ratio": beta_power_closed_over_open,
            "beta_alpha_ratio_closed_over_open": beta_alpha_ratio_closed_over_open,
            "beta_alpha_ratio_open_over_closed": beta_alpha_ratio_open_over_closed,
        }
    ]

    comparison_csv_path = (
        RESULT_DIR
        / "subject-001_bandpower_condition_comparison.csv"
    )

    with open(comparison_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "subject",
            "comparison",
            "alpha_power_ratio",
            "beta_power_ratio",
            "beta_alpha_ratio_closed_over_open",
            "beta_alpha_ratio_open_over_closed",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparison_rows)

    print("Saved condition comparison CSV:", comparison_csv_path)
    print("Alpha power closed/open ratio:", alpha_power_closed_over_open)
    print("Beta power closed/open ratio:", beta_power_closed_over_open)
    print("Beta/Alpha ratio closed/open:", beta_alpha_ratio_closed_over_open)
    print("Beta/Alpha ratio open/closed:", beta_alpha_ratio_open_over_closed)

    # alpha/beta power를 조건별 bar plot으로 시각화
    conditions = [row["condition"] for row in band_power_rows]
    alpha_powers = [row["alpha_power"] for row in band_power_rows]
    beta_powers = [row["beta_power"] for row in band_power_rows]

    x_positions = list(range(len(conditions)))
    bar_width = 0.35

    plt.figure(figsize=(10, 6))

    # alpha power bar
    plt.bar(
        [x - bar_width / 2 for x in x_positions],
        alpha_powers,
        width=bar_width,
        label="alpha power (8–13 Hz)"
    )

    # beta power bar
    plt.bar(
        [x + bar_width / 2 for x in x_positions],
        beta_powers,
        width=bar_width,
        label="beta power (13–30 Hz)"
    )

    plt.xticks(x_positions, conditions)
    plt.xlabel("Condition")
    plt.ylabel("Mean PSD")
    plt.title("Alpha/Beta Power Comparison: Eyes Open vs Eyes Closed")
    plt.legend()
    plt.tight_layout()

    bandpower_fig_path = (
        FIGURE_DIR
        / "subject-001_alpha_beta_power_comparison.png"
    )

    plt.savefig(bandpower_fig_path, dpi=150)
    plt.close()

    print("Saved alpha/beta power comparison figure:", bandpower_fig_path)

    # eyes open / eyes closed posterior mean PSD를 한 그래프에 비교
    plt.figure(figsize=(10, 6))

    for run in RUNS:
        plt.plot(
            freqs_by_run[run],
            posterior_mean_psd_by_run[run],
            label=RUN_LABELS[run]
        )

    # alpha band 영역 표시
    plt.axvspan(8, 13, alpha=0.2, label="alpha band (8–13 Hz)")

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power Spectral Density")
    plt.title("Posterior Mean PSD Comparison: Eyes Open vs Eyes Closed")
    plt.legend()
    plt.tight_layout()

    comparison_fig_path = (
        FIGURE_DIR
        / "subject-001_eyes_open_vs_eyes_closed_posterior_mean_psd.png"
    )

    plt.savefig(comparison_fig_path, dpi=150)
    plt.close()

    print("Saved PSD comparison figure:", comparison_fig_path)