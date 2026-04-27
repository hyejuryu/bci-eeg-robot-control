# EEG Frequency Bands and Rhythms

## Purpose

EEG 신호의 주요 주파수 대역과 rhythm 개념을 정리하고, 각 대역을 BCI feature로 해석할 때의 기준과 한계를 구분한다.

- EEG 신호 파악의 주의점
- frequency band와 rhythm의 차이
- 정상 EEG pattern과 artifact의 차이
- 생리학적 설명과 실제 feature 해석의 차이
- 초기 BCI feature로 사용할 수 있는 대역과 보류해야 할 대역

## Core Structure

| Domain | Key components | What matters for EEG/BCI |
| --- | --- | --- |
| EEG observation | waveform, amplitude, frequency, distribution, phase, synchrony, reactivity | EEG는 단일 주파수 값이 아니라 여러 특성이 결합된 패턴이다 |
| Signal unit | wave, rhythm, background activity | frequency band와 rhythm은 구분해야 한다 |
| Normal adult EEG | posterior alpha, low-amplitude beta, symmetry | baseline과 condition 차이를 구분해야 한다 |
| Reactivity | alpha blocking, task-related change | BCI feature는 조건 변화에 반응해야 한다 |
| Artifact | eye blink, eye movement, EMG, movement, line noise | feature extraction 이전에 noise와 artifact를 확인해야 한다 |

## Key Points

### 1. EEG는 주파수 하나로 해석할 수 없다

EEG 분석에서는 주파수뿐 아니라 파형 모양, 진폭, 분포, 위상관계, 동기성, 지속성, 반응성을 함께 봐야 한다.

예를 들어 특정 채널에서 10 Hz activity가 관찰되었다고 해서 곧바로 “alpha rhythm이 나타났다”고 말할 수는 없다.  
그 activity가 어느 위치에서 나타났는지, eyes closed / eyes open 조건에 반응하는지, 정상적인 배경파의 일부인지 함께 확인해야 한다.

따라서 EEG feature는 단일 값이 아니라 조건에 따라 변하는 pattern으로 보는 것이 적절하다.

### 2. Frequency band와 rhythm은 구분해야 한다

Frequency band는 특정 주파수 범위를 의미한다.  
반면 rhythm은 특정 주파수 범위뿐 아니라 위치, 파형, 규칙성, 반응성까지 포함하는 개념이다.

| Concept | Meaning |
| --- | --- |
| Alpha band | 8–13 Hz 범위의 EEG activity |
| Alpha rhythm | 정상 성인의 awake, relaxed, eyes-closed 상태에서 주로 후두부에 나타나며, eyes open 또는 정신활동에 의해 감소하는 리듬 |

따라서 BCI 분석에서는 “8–13 Hz power가 증가했다”와 “alpha rhythm이 관찰되었다”를 구분해야 한다.

### 3. Alpha rhythm은 초기 EEG 분석에서 가장 먼저 확인할 수 있는 기준 신호다

정상 성인에서 alpha rhythm은 주로 awake, relaxed, eyes-closed 상태에서 후두부를 중심으로 나타난다.  
눈을 뜨거나, 시각 자극을 처리하거나, 간단한 정신활동을 수행하면 alpha activity가 감소할 수 있다. 이를 alpha blocking 또는 alpha suppression으로 볼 수 있다.

BCI 관점에서 alpha rhythm이 중요한 이유는 다음과 같다.

- eyes closed / eyes open 조건으로 비교적 단순하게 확인할 수 있다.
- 장비와 전극 세팅이 정상적으로 작동하는지 확인하는 기준이 될 수 있다.
- rest condition과 active condition의 차이를 보는 초기 feature가 될 수 있다.
- focus-state feature를 보기 전 baseline reactivity를 확인할 수 있다.

따라서 초기 EEG 분석에서는 alpha reactivity를 먼저 확인하는 것이 합리적이다.


## Frequency Bands in BCI Perspective

| Band / Rhythm | Frequency range | General context | Possible BCI use | Main caution |
| --- | --- | --- | --- | --- |
| Delta | ~0.5–4 Hz | 깊은 수면, 느린 활동 | 초기 focus BCI에서는 주요 feature 아님 | 눈 움직임, 움직임 artifact와 혼동 가능 |
| Theta | ~4–8 Hz | 졸림, 이완, 정서, 작업기억 등 | 보조 feature 가능 | 의미 범위가 넓어 단독 해석 위험 |
| Alpha | ~8–13 Hz | eyes-closed relaxed wakefulness, posterior rhythm | EEG 품질 확인, rest/focus 비교 | band와 rhythm 구분 필요 |
| SMR | ~12–15 Hz | 감각운동 영역의 안정적 rhythm | 향후 motor imagery, robot control과 연결 가능 | posterior alpha, beta와 구분 필요 |
| Low beta | ~14–20 Hz or 16–20 Hz | alertness, problem solving, task engagement | focus-state 후보 feature | EMG, 긴장, 불안과 혼동 가능 |
| High beta | ~20–30 Hz 이상 | 긴장, 불안, 고각성, 약물 영향 가능 | 초기 feature로는 주의 필요 | muscle artifact 가능성 증가 |
| Gamma | ~30–50 Hz 이상 | 고차 인지, binding, peak performance 후보 | 장기 연구 후보 | artifact 위험이 커 초기 threshold feature로 부적합 |

## Artifact Relevance

EEG에는 뇌에서 발생한 신호뿐 아니라 다양한 artifact가 섞인다.  
artifact를 구분하지 못하면 beta나 gamma 증가를 실제 인지적 변화로 잘못 해석할 수 있다.

| Artifact source | Common effect | Can be confused with |
| --- | --- | --- |
| Eye blink | 큰 저주파 deflection | delta / theta |
| Eye movement | 전두부 저주파 변화 | slow wave activity |
| Muscle tension | 고주파 activity 증가 | beta / gamma |
| Jaw clenching | broad high-frequency noise | high beta / gamma |
| Movement | 불규칙한 큰 파형 변화 | transient EEG event |
| Poor electrode contact | drift, unstable amplitude | abnormal EEG |
| Power line noise | 50/60 Hz peak | high-frequency activity |

따라서 feature를 보기 전에 raw signal과 artifact를 먼저 확인해야 한다.

## Interpretation Boundary

| Observation | Acceptable interpretation | Over-interpretation to avoid |
| --- | --- | --- |
| Alpha power decreased | 해당 조건에서 alpha band power가 감소했다 | 피험자가 반드시 집중했다 |
| Low beta increased | task condition에서 low beta power가 증가했다 | 문제 해결 능력이 향상되었다 |
| Beta/Alpha ratio increased | focus score 후보 값이 증가했다 | 의식 수준이 상승했다 |
| Gamma activity observed | high-frequency activity가 관찰되었다 | 고차 인지나 peak performance가 증명되었다 |
| Threshold crossed | feature value가 기준값을 넘었다 | 뇌의 의도 자체를 직접 읽었다 |

## Implication for BCI

이번 정리를 바탕으로 초기 BCI feature 후보는 다음 순서로 두는 것이 적절하다.

1. Alpha reactivity
   - eyes closed / eyes open 조건에서 확인
   - EEG 품질과 상태 반응성 확인

2. Alpha suppression
   - rest 또는 baseline 대비 active condition에서 감소하는지 확인
   - focus-state 후보 feature의 기본 기준

3. Low beta band power
   - 14–20 Hz 또는 16–20 Hz 범위의 power 변화 확인
   - 문제 해결 또는 과제 수행 상태의 후보 feature

4. Beta/Alpha ratio
   - alpha 감소와 beta 증가를 하나의 score로 결합하는 후보
   - threshold 기반 제어로 연결 가능하지만 과도한 단순화 주의

5. Gamma/40 Hz
   - 장기 연구 후보
   - 초기 threshold feature에서는 제외

## Next Analysis Block

다음 단계는 직접 실험이 아니라 공개 EEG 데이터와 Python 분석 환경을 활용한 기초 분석이다.

우선 확인해야 할 항목은 다음과 같다.

- EEG file format
- sampling rate
- channel names
- reference 방식
- event marker 또는 condition label
- raw signal amplitude range
- noisy channel 여부
- eye blink, eye movement, EMG artifact
- band-pass filtering 전후 waveform 변화
- FFT 또는 power spectrum
- alpha power와 low beta power의 조건별 변화

## Summary

EEG 대역은 BCI feature 설계의 출발점이지만, 각 대역을 심리 상태와 직접 연결해서는 안 된다.

현재 단계에서 가장 중요한 결론은 다음과 같다.

- EEG는 주파수 하나가 아니라 여러 특성이 결합된 pattern이다.
- Frequency band와 rhythm은 구분해야 한다.
- Alpha reactivity는 초기 EEG 품질 확인과 상태 변화 확인에 가장 유용하다.
- Low beta는 focus-state 후보 feature가 될 수 있지만, 단일 17 Hz threshold보다 band power로 다루는 것이 적절하다.
- Gamma/40 Hz는 장기 후보로 남기되, 초기 feature에서는 보류한다.
- 공개 EEG 데이터를 분석할 때는 feature extraction보다 raw signal과 artifact 확인이 먼저다.
