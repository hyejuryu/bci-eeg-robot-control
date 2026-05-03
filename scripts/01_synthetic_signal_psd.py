# 일부러 10 Hz와 20 Hz 성분이 들어간 가짜 신호를 만들고,
# 그 신호를 PSD로 바꾼 뒤, alpha/beta 구간의 power를 계산하고,
# 그 결과를 그림과 텍스트 파일로 저장한다.

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch


# 1. Output folders
# 결과 저장 폴더 만들기
output_dir = Path("figures") / "session-05"
output_dir.mkdir(parents=True, exist_ok=True)

results_dir = Path("results") / "session-05"
results_dir.mkdir(parents=True, exist_ok=True)


# 2. Basic signal settings
# Sampling frequency와 duration 설정
# Sampling frequency: EEGBCI 공개 데이터셋과 맞추기 위해 160 Hz 사용
# OpenBCI Cyton 8-Channel board 등 실제 데이터에서는 장비/파일의 sampling rate를 확인해서 입력해야 함
sfreq = 160
duration = 10

# 시간축을 만드는 코드
# 0초부터 duration초 전까지, 1/sfreq초 간격으로 시간값을 생성
t = np.arange(0, duration, 1 / sfreq) # len(t) = 1600 time points


# 3. Synthetic EEG-like signal
# This is NOT real EEG.
# It is only a test signal for checking the analysis pipeline.
# 가짜 signal을 만들었을 때 분석 코드가 그 주파수 성분을 찾아낼 수 있는지 확인하는 테스트
# 10 Hz alpha-like component + 20 Hz beta-like component + noise

rng = np.random.default_rng(42)

# 사인파를 이용해서 시간에 따른 가짜 신호값 생성
# amplitude * np.sin(2 * np.pi * frequency * t)

alpha = 1.0 * np.sin(2 * np.pi * 10 * t) # 10Hz짜리 사인파
beta = 0.4 * np.sin(2 * np.pi * 20 * t) # 20Hz짜리 사인파 #10Hz 파형보다 빠르지만 작게 흔들리는 20Hz 파형
noise = 0.5 * rng.standard_normal(t.shape) #랜덤 잡음

signal = alpha + beta + noise


# 4. Power Spectral Density using Welch's method
# Welch 방법으로 PSD 계산
# PSD: 어떤 주파수에 신호의 power가 얼마나 분포해 있는지 나타낸 것
# Welch PSD: signal을 여러 조각으로 나누고,
# 각 조각의 periodogram을 구한 뒤,
# 그것들을 평균해서 더 안정적인 PSD 추정값을 얻는 방법

# periodogram: Fourier transform 결과를 이용해서 각 주파수의 power를 추정한 것

freqs, psd = welch(signal, fs=sfreq, nperseg=sfreq * 2) #2초짜리 조각


# 5. Define frequency bands
# 전체 PSD 중 alpha/beta frequency band 정의
# 경계가 겹치지 않도록 alpha는 13 Hz 미만, beta는 13 Hz 이상으로 설정
alpha_band = (freqs >= 8) & (freqs < 13)
beta_band = (freqs >= 13) & (freqs <= 30)


# 6. Calculate band power
# alpha/beta power: 해당 주파수 구간 아래 면적 계산
alpha_power = np.trapezoid(psd[alpha_band], freqs[alpha_band])
beta_power = np.trapezoid(psd[beta_band], freqs[beta_band])
beta_alpha_ratio = beta_power / alpha_power


# 7. Print and save numerical results
# 터미널에 출력되는 숫자 결과를 텍스트 파일로도 저장
summary_text = f"""Synthetic EEG-like Signal PSD Summary

Sampling frequency: {sfreq} Hz
Signal duration: {duration} seconds
Number of samples: {len(signal)}

Alpha band: 8 <= f < 13 Hz
Beta band: 13 <= f <= 30 Hz

Alpha power: {alpha_power:.4f}
Beta power: {beta_power:.4f}
Beta / Alpha ratio: {beta_alpha_ratio:.4f}

Note:
This is not real EEG data.
This synthetic signal was used only to test the analysis pipeline.
"""

print(summary_text)

summary_path = results_dir / "synthetic_signal_psd_summary.txt"
summary_path.write_text(summary_text, encoding="utf-8")


# 8. Plot time-domain signal
# time-domain 그래프: 시간에 따라 신호가 어떻게 흔들리는지 보여줌
# 원래 signal의 시간 표현
# signal = 시간 또는 공간에 따라 변하는 측정값. / EEG signal = 시간에 따라 기록된 전압 변화
plt.figure(figsize=(10, 4))
plt.plot(t, signal)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Synthetic EEG-like Signal")
plt.tight_layout()
plt.savefig(output_dir / "synthetic_signal_time_series.png", dpi=150)


# 9. Plot frequency-domain PSD
# frequency-domain 그래프: 어떤 주파수에 power가 많은지 보여줌
# PSD로 요약한 주파수 표현
plt.figure(figsize=(10, 4))
plt.semilogy(freqs, psd)
plt.axvspan(8, 13, color="gold", alpha=0.25, label="Alpha band")
plt.axvspan(13, 30, color="lightgreen", alpha=0.25, label="Beta band")
plt.xlabel("Frequency (Hz)")
plt.ylabel("PSD")
plt.title("Power Spectral Density")
plt.legend()
plt.tight_layout()
plt.savefig(output_dir / "synthetic_signal_psd.png", dpi=150)

plt.show()