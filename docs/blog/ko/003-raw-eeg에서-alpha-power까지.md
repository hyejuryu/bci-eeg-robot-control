# Raw EEG에서 Alpha Power까지: 첫 EEG 분석 파이프라인 만들기

*OpenBCI 데이터를 직접 수집하기 전, synthetic signal과 공개 EEG 데이터로 분석 흐름을 먼저 검증한 기록.*

EEG 기반 BCI를 처음 공부하기 시작했을 때, 이 프로젝트는 아직 대부분 개념적인 수준에 머물러 있었다.

나는 brain state, attention, signal feature, threshold, robot control 같은 단어들을 생각하고 있었다. 하지만 그때의 EEG는 주로 그림과 설명으로 이해하는 대상에 가까웠다.

이 관점은 실제 signal data를 다루기 시작하면서 바뀌었다.

이번 EEG-BCI robot control project의 두 번째 마일스톤은 아직 로봇을 제어하는 단계가 아니었다. OpenBCI로 내 데이터를 직접 수집하는 단계도 아니었다.

이번 마일스톤의 목표는 첫 번째 분석 경로를 실제로 만들어보는 것이었다.

```text
signal
→ data structure
→ frequency-domain representation
→ band power feature
→ condition comparison
```

OpenBCI Cyton 8-channel board를 사용하기 전에, 나는 더 단순한 질문에 먼저 답하고 싶었다.

> EEG 데이터를 불러와 구조를 확인하고, frequency-domain feature로 변환한 뒤, 기본적인 조건 차이를 관찰할 수 있는가?

이번 마일스톤에서는 공개 EEG 데이터셋을 사용했고, 가장 기본적인 비교 조건에 집중했다.

```text
eyes open
vs.
eyes closed
```

목표는 “focus”를 감지하거나 mental state를 읽는 것이 아니었다.

더 현실적인 목표는 다음과 같았다.

> Raw EEG에서 측정 가능한 feature로 이어지는 신뢰 가능한 분석 경로를 만드는 것.

## 왜 바로 OpenBCI부터 시작하지 않았는가

BCI 프로젝트를 시작하면 곧바로 하드웨어를 연결하고 싶어진다.

그게 더 흥미로워 보인다. 하지만 동시에 더 위험하다.

분석 pipeline을 충분히 이해하지 못한 상태에서 noisy한 EEG 데이터를 수집하면, 결과가 실패했을 때 원인을 구분하기 어렵다. 문제가 전극 세팅에 있는지, 코드에 있는지, feature 정의에 있는지, preprocessing에 있는지, 실험 설계에 있는지 알기 힘들다.

그래서 먼저 문제를 작은 단계로 나누기로 했다.

내 데이터를 수집하기 전에 먼저 이해해야 할 것은 다음과 같았다.

- EEG-like time-series signal이 Python에서 어떻게 표현되는가
- sampling frequency가 time과 sample index에 어떻게 연결되는가
- power spectrum을 어떻게 계산하는가
- alpha/beta band power를 어떻게 추출하는가
- 실제 EEG 데이터는 어떤 구조로 저장되어 있는가
- 왜 raw EEG waveform만 보는 것으로는 부족한가
- eyes-open / eyes-closed 조건을 PSD로 어떻게 비교할 수 있는가

이것은 단순한 준비 작업이 아니었다.

실제 연구 workflow의 시작이었다.

## Step 1: Synthetic signal로 pipeline을 먼저 테스트하기

첫 번째 단계는 간단한 분석 환경을 만들고, 기본 signal-processing 코드가 작동하는지 확인하는 것이었다.

나는 세 가지 성분을 합쳐 synthetic EEG-like signal을 만들었다.

```text
10 Hz alpha-like sine wave
20 Hz beta-like sine wave
random noise
```

이것은 실제 EEG가 아니다.

이 구분은 중요하다.

Synthetic signal은 생리학적 의미의 alpha rhythm이나 beta activity를 보여주는 것이 아니다. 이미 어떤 주파수 성분이 들어 있는지 알고 있는 controlled signal일 뿐이다.

그래서 synthetic signal은 smoke test로 유용하다.

강한 10 Hz 성분과 더 작은 20 Hz 성분을 가진 signal을 만들었다면, PSD에서는 10 Hz 근처의 큰 peak와 20 Hz 근처의 작은 peak가 보여야 한다. 만약 코드가 이것조차 찾지 못한다면, 실제 EEG 데이터에 적용하기 전에 먼저 코드를 의심해야 한다.

[Figure 01: `figures/session-05/synthetic_signal_psd.png`](../figures/session-05/synthetic_signal_psd.png)

Synthetic signal은 기본적이지만 중요한 사실을 이해하는 데 도움이 되었다.

> Time domain에서 복잡해 보이는 signal도 frequency domain에서는 더 해석 가능해질 수 있다.

Time-domain graph에서는 signal이 noisy하고 irregular한 파형처럼 보인다.

하지만 PSD graph에서는 frequency structure가 드러난다.

이것이 EEG에서 frequency-domain analysis가 중요한 첫 번째 이유다.

Raw EEG는 보통 깨끗하거나 눈으로 명확하게 보이지 않는다. alpha power나 beta power를 이야기하려면, time-series signal을 frequency-domain representation으로 변환해야 한다.

## Step 2: 실제 EEG 데이터 열기

Synthetic signal test 이후에는 공개 EEG 데이터셋으로 넘어갔다.

MNE-Python을 이용해 EEGBCI dataset을 불러왔고, Subject 1의 baseline eyes-open run과 eyes-closed run을 사용했다.

이 단계는 feature extraction보다 덜 화려하지만, 필수적이었다.

EEG를 해석하기 전에 먼저 raw data structure를 확인해야 했다.

- sampling frequency
- channel names
- number of channels
- number of samples
- recording duration
- annotations
- data shape

이번에 가장 중요하게 배운 점 중 하나는 EEG가 연속적인 “뇌파 그림”으로 저장되어 있지 않다는 것이다.

Python 내부에서 EEG는 numerical time-series data다.

이번 데이터셋의 sampling frequency는 160 Hz였다.

즉:

```text
1 second = 160 samples
```

따라서 EEG 10초를 시각화한다는 것은, 실제로는 약 1600개의 sample point를 선택해 시간축 위에 그린다는 뜻이다.

이 점은 EEG를 바라보는 방식을 바꾸었다.

EEG를 신비로운 waveform으로 상상하기보다, 구조를 가진 numerical data로 보기 시작했다.

```text
channels × samples
```

[Figure 02: `figures/session-06/subject-001_run-01_baseline_eyes_open_first_10s.png`](../figures/session-06/subject-001_run-01_baseline_eyes_open_first_10s.png)

Raw waveform은 noisy했다.

깨끗한 sine wave처럼 보이지 않았다. fluctuation이 있었고, channel마다 형태가 달랐으며, amplitude도 불규칙하게 변했다.

하지만 완전히 random하게 보이지도 않았다.

이것은 중요한 지점이었다. EEG는 noisy biological data이지만, 동시에 structured data다.

문제는 waveform을 과해석하지 않으면서 그 안에서 유용한 구조를 어떻게 추출할 것인가다.

## 왜 raw EEG waveform만으로는 부족한가

Raw EEG를 보는 것은 중요하다. 하지만 그것만으로는 충분하지 않다.

Eyes-open과 eyes-closed raw waveform을 시각적으로 비교했을 때, 신호가 약간 다르게 보일 수는 있었다. 하지만 raw waveform만 보고 다음과 같이 말할 수는 없었다.

```text
alpha increased
beta decreased
```

이런 해석을 하려면 frequency-domain analysis가 필요하다.

이번 마일스톤에서 가장 중요한 교훈 중 하나는 다음과 같다.

> Raw EEG visualization과 EEG rhythm analysis는 같은 일이 아니다.

Waveform은 조건에 따라 다르게 보일 수 있다. 하지만 alpha와 beta는 frequency-domain feature다. 이를 분석하려면 power spectrum을 계산하고, 정의된 frequency band 안에서 power를 요약해야 한다.

그래서 분석 경로는 다음과 같이 정리되었다.

```text
raw EEG
→ band-pass filtering
→ posterior channel selection
→ Welch PSD
→ posterior mean PSD
→ alpha/beta band power
→ eyes-open vs eyes-closed comparison
```

이것이 내 EEG analysis pipeline의 첫 번째 실제 버전이다.

## Step 3: Frequency domain으로 이동하기

실제 EEG 분석에서는 1–40 Hz band-pass filtering을 적용하고, posterior channel을 선택했다.

Posterior channel을 사용한 이유는 eyes-closed / eyes-open 비교에서 alpha reactivity가 후두부 및 posterior region에서 더 뚜렷하게 나타나는 경우가 많기 때문이다.

이후 Welch method를 이용해 Power Spectral Density를 계산했다.

Welch PSD는 signal power가 frequency별로 어떻게 분포하는지 추정한다. 이제 amplitude가 시간에 따라 어떻게 변하는지를 보는 대신, 다음 질문을 할 수 있다.

> 어떤 frequency range에 power가 더 많이 분포하는가?

이번 분석에서는 다음과 같이 frequency band를 정의했다.

```text
alpha band: 8 Hz ≤ f < 13 Hz
beta band: 13 Hz ≤ f ≤ 30 Hz
```

PSD data는 다음 구조를 가지고 있었다.

```text
6 posterior channels × 500 frequency points
```

이 세부 사항은 중요하다.

PSD는 단순한 graph가 아니다. PSD는 array다.

Frequency axis는 spectrum에서의 위치를 알려주고, PSD values는 각 channel이 각 frequency point에서 어느 정도 power를 가지는지 보여준다.

Posterior channel들에 대해 평균을 내면, 각 조건별 posterior mean PSD를 얻을 수 있다.

이를 통해 eyes-open condition과 eyes-closed condition을 더 직접적으로 비교할 수 있었다.

## 첫 번째 sanity check로서의 alpha reactivity

주요 결과는 명확했다.

```text
eyes closed → stronger posterior alpha peak around 10 Hz
eyes open   → much lower posterior alpha power
```

[Figure 03: `figures/session-07/subject-001_eyes_open_vs_eyes_closed_posterior_mean_psd.png`](../figures/session-07/subject-001_eyes_open_vs_eyes_closed_posterior_mean_psd.png)

Subject 1 분석에서 posterior alpha power는 eyes-closed condition에서 eyes-open condition보다 훨씬 높게 나타났다.

Eyes-closed condition의 alpha power는 eyes-open condition보다 약 11.5배 높았다.

Beta power도 eyes-closed condition에서 증가했지만, 그 증가 폭은 alpha power보다 작았다. alpha power가 훨씬 더 크게 증가했기 때문에 beta/alpha ratio는 eyes-closed condition에서 더 낮아졌다.

[Figure 04: `figures/session-07/subject-001_alpha_beta_power_comparison.png`](../figures/session-07/subject-001_alpha_beta_power_comparison.png)

이 결과는 고무적이었다. 분석 pipeline이 기본적이고 예상 가능한 condition-dependent spectral difference를 잡아낼 수 있음을 보여주었기 때문이다.

하지만 해석은 제한되어야 한다.

이 결과는 시스템이 mental state를 읽었다는 뜻이 아니다.

다음과 같은 의미도 아니다.

```text
eyes closed = relaxation
eyes open = focus
```

더 조심스러운 해석은 다음과 같다.

> 이 공개 EEG 데이터셋에서, posterior alpha-band power는 정의된 eyes-closed baseline condition과 eyes-open baseline condition 사이에서 다르게 나타났다.

덜 극적이지만, 더 과학적으로 유용한 표현이다.

## 왜 이것이 OpenBCI 전에 중요한가

Alpha reactivity 결과는 이 프로젝트의 최종 목표가 아니다.

이 프로젝트의 최종 목표는 OpenBCI로 EEG를 수집하고, Python에서 feature를 추출한 뒤, decision rule을 Arduino-based robot control로 연결하는 것이다.

하지만 그 전에 sanity check가 필요하다.

정리된 공개 EEG 데이터에서 기본적인 eyes-open / eyes-closed alpha difference도 관찰하지 못한다면, 내 OpenBCI recording에서 안정적인 real-time control을 기대하는 것은 너무 이르다.

Alpha reactivity는 첫 번째 checkpoint 역할을 한다.

```text
Can the pipeline detect a known physiological condition difference?
```

이 질문에 어느 정도 답할 수 있다면, 그다음에는 더 어려운 질문으로 넘어갈 수 있다.

- 내 OpenBCI data에서도 비슷한 alpha reactivity를 관찰할 수 있는가?
- Feature는 time window에 따라 얼마나 안정적인가?
- 같은 condition 안에서도 feature는 얼마나 변동하는가?
- Alpha suppression이나 low beta power가 rest/task condition을 구분할 수 있는가?
- 실제 feature distribution을 보고 threshold를 설정할 수 있는가?
- Real-time control에서 false trigger는 얼마나 발생할 수 있는가?

이 질문들은 단순히 어떤 feature value가 높거나 낮은지를 보는 것보다 중요하다.

## Classification보다 signal dynamics로 보기

현재 단계에서 나는 mental state를 labeling하는 classifier를 만들려는 것이 아니다.

그렇게 하기에는 아직 이르다.

대신 나는 정의된 조건 아래에서 EEG feature가 어떻게 변하는지 이해하려고 한다.

이 구분은 프로젝트의 장기적인 방향에서도 중요하다.

기본적인 BCI demo는 나중에 다음과 같은 rule을 사용할 수도 있다.

```python
if beta_power > threshold:
    send_command_to_robot()
```

하지만 이 rule은 feature가 충분히 안정적이고, 조건 사이에서 충분히 구분 가능하며, 실험 맥락 안에서 해석 가능할 때에만 의미가 있다.

향후 단계에서는 single-value comparison에서 window-based analysis로 넘어가야 한다.

전체 recording에서 alpha나 beta 값을 하나만 계산하는 것이 아니라, 짧은 sliding window마다 feature를 계산해야 한다.

```text
0–2 s
1–3 s
2–4 s
3–5 s
...
```

그러면 feature가 시간에 따라 어떻게 변하는지 볼 수 있다.

이것이 중요한 이유는 real-time BCI system이 실험이 끝난 뒤의 전체 평균값으로 작동하지 않기 때문이다. 실시간 시스템은 signal이 변하는 중에 판단을 내려야 한다.

장기적으로는 feature가 단순히 높은지 낮은지만이 아니라, 조건 전환 과정에서 EEG feature가 시간에 따라 어떻게 evolve하는지 보고 싶다.

하지만 지금 단계의 첫 번째 목표는 더 단순하다.

> Raw signal에서 measurable feature로 이어지는 신뢰 가능한 경로를 만드는 것.

## 이번 마일스톤에서 배운 것

이번 마일스톤에서 가장 큰 변화는 EEG가 덜 추상적인 대상이 되었다는 점이다.

첫 번째 마일스톤에서는 EEG가 무엇인지, 그리고 왜 EEG를 mind reading처럼 해석하면 안 되는지를 공부했다.

이번 마일스톤에서는 EEG를 실제 data로 다루기 시작했다.

가장 중요한 교훈은 다음과 같다.

```text
EEG is not just a waveform.
It is structured numerical time-series data.
```

그리고 EEG analysis는 단순히 plotting하는 일이 아니다.

EEG analysis에는 여러 선택이 포함된다.

```text
sampling frequency
channel selection
time window
filtering range
PSD method
frequency bands
feature calculation
condition comparison
interpretation boundary
```

각 선택은 결론에 영향을 준다.

그래서 EEG에서 robot control로 곧바로 뛰어넘고 싶지 않다.

Signal은 command가 되기 전에 measurement, transformation, feature extraction, decision-making을 거쳐야 한다.

## 현재 상태

이번 마일스톤이 끝난 시점에서, 나는 기본적인 offline EEG analysis pipeline을 갖게 되었다.

```text
environment setup
→ synthetic signal test
→ public EEG loading
→ raw EEG inspection
→ band-pass filtering
→ Welch PSD
→ alpha/beta band power
→ eyes-open vs eyes-closed comparison
→ figure and CSV export
```

아직 작은 단계다.

하지만 중요한 단계다.

이제 OpenBCI data collection으로 넘어갈 때 사용할 수 있는 명확한 baseline이 생겼다.

```text
eyes open
vs.
eyes closed
→ posterior alpha power difference
```

Focus-based robot control을 시도하기 전에, 먼저 내 hardware setup에서도 이 기본 반응을 재현할 수 있는지 확인해야 한다.

그것이 가능해지면 task condition, sliding-window feature, threshold design, real-time control로 넘어갈 수 있다.

## Conclusion

이번 마일스톤은 EEG로 robot을 제어할 수 있음을 증명하는 단계가 아니었다.

이번 마일스톤은 EEG를 분석 가능한 대상으로 만드는 단계였다.

나는 먼저 주파수 성분을 알고 있는 synthetic signal에서 시작했다. 그다음 실제 EEG 데이터를 열고 구조를 확인했다. 마지막으로 공개 EEG recording을 frequency-domain feature로 변환했고, eyes-closed condition과 eyes-open condition 사이에서 posterior alpha difference를 관찰했다.

중요한 결과는 “relaxation을 감지했다”거나 “focus를 읽었다”는 것이 아니다.

중요한 결과는 첫 번째 bridge를 만들었다는 것이다.

```text
raw EEG
→ structured data
→ frequency-domain feature
→ condition comparison
```

초기 EEG-BCI 프로젝트에서는 극적인 demo보다 이 bridge가 더 중요하다.

Robot은 내가 EEG의 의미를 추측했기 때문에 움직이면 안 된다.

Signal이 측정되고, 변환되고, 테스트되고, decision rule을 지탱할 만큼 안정적인 feature로 줄어든 뒤에야 robot command로 이어져야 한다.

그것이 다음 과제다.

---

## Note

This post is based on my Session 05–07 study notes from an EEG-BCI robot control project.

At this stage, the goal is not to make strong claims about attention, relaxation, or cognition. The goal is to build a careful signal analysis pipeline before collecting OpenBCI data and attempting real-time robot control.

## Project Repository

The project notes and session logs are archived on GitHub:

[EEG-BCI Robot Control Project](GITHUB_REPOSITORY_LINK)

## References / Study Notes

This post is based on my Session 05–07 study notes from an EEG-BCI robot control project.

Additional references:

- [MNE-Python documentation](https://mne.tools/stable/index.html)
- [MNE EEGBCI dataset documentation](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html)
- [SciPy documentation: `scipy.signal.welch`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html)
- [PhysioNet EEG Motor Movement/Imagery Dataset](https://physionet.org/content/eegmmidb/1.0.0/)
- [NumPy documentation](https://numpy.org/doc/stable/)
- [Matplotlib documentation](https://matplotlib.org/stable/)
