# Focus-State Feature Candidates and Selection Criteria

## Purpose

집중 상태 기반 BCI에서 사용할 수 있는 EEG feature 후보를 정리하고, 각 feature의 기대 변화, 사용 가능성, 한계, 초기 우선순위를 구분한다.

이번 문서의 목적은 “집중”을 직접 측정한다고 가정하는 것이 아니라, rest 또는 baseline condition과 비교했을 때 반복적으로 관찰 가능한 EEG feature 변화를 정리하는 것이다.

핵심 질문은 다음과 같다.

- 집중 상태 기반 BCI에서 우선 검토할 수 있는 EEG feature는 무엇인가?
- 각 feature는 어떤 조건에서 어떤 변화 패턴을 보일 것으로 예상되는가?
- 어떤 feature를 초기 분석에서 우선 사용하고, 어떤 feature는 보류해야 하는가?
- 이후 공개 EEG 데이터 분석에서 어떤 feature를 먼저 확인해야 하는가?

## Core Structure

| Domain | Key components | What actually matters | Why it matters for EEG/BCI |
| --- | --- | --- | --- |
| Focus-state definition | rest, baseline, task condition | 집중은 직접 측정되는 대상이 아니라 조건 비교를 통해 추론되는 상태다 | feature를 조작적으로 정의해야 한다 |
| Feature selection | alpha, low beta, ratio, theta, gamma | 모든 대역을 같은 우선순위로 볼 수 없다 | 초기 분석에 적합한 feature를 좁혀야 한다 |
| Reactivity | alpha suppression, beta increase | 조건 변화에 따라 feature가 반복적으로 변하는지가 중요하다 | threshold 또는 classifier의 입력이 된다 |
| Robustness | artifact, 개인차, baseline | feature가 noise와 구분되어야 한다 | 잘못된 feature는 false trigger를 만든다 |
| Initial analysis | public EEG dataset, raw signal, filtering, PSD | 실제 데이터에서 feature가 관찰되는지 확인해야 한다 | 이론적 후보를 데이터 기반 후보로 좁힌다 |

## Candidate Feature List

| Candidate feature | Expected pattern | Possible electrodes / regions | Why useful | Risk / limitation | Initial priority |
| --- | --- | --- | --- | --- | --- |
| Alpha power | focus 또는 task 조건에서 감소 가능 | O1, O2, Oz, Pz 등 posterior 중심 | 비교적 안정적으로 관찰 가능하며, eyes closed / eyes open 조건에서 반응성 확인 가능 | 눈감음, 시각 조건, 졸림의 영향이 큼 | High |
| Alpha suppression | rest 또는 baseline 대비 task 조건에서 감소 | posterior, parietal, 일부 central | 상태 변화와 task engagement를 포착하기 쉬움 | baseline 설정이 불안정하면 해석 어려움 | High |
| Low beta power | 문제 해결, 계산, 주의 과제에서 증가 가능 | frontal, central, parietal 후보 | focus-state 후보 feature로 검토 가능 | EMG, 긴장, 불안과 혼동 가능 | Medium-High |
| Beta / Alpha ratio | focus/rest 차이를 하나의 score로 단순화 가능 | frontal, central, parietal 후보 | threshold 기반 제어로 연결하기 쉬움 | alpha 감소만으로도 ratio가 증가할 수 있어 과도한 단순화 위험 | Medium |
| Theta power | 졸림, 이완, 작업기억, 정서 상태 등에서 변화 가능 | Fz, Cz 등 frontal-midline / central 후보 | 보조적 상태 지표로 사용 가능 | 의미 범위가 넓어 단독 해석 위험 | Low-Medium |
| Theta / Beta ratio | attention-related index 후보 | Fz, Cz 등 frontal-midline / central 후보 | 주의 상태 관련 보조 지표로 검토 가능 | ADHD 등 임상 맥락과 혼동 주의 | Low-Medium |
| SMR power | 안정된 감각운동 상태에서 증가, 움직임 또는 운동상상 시 감소 가능 | C3, Cz, C4 등 sensorimotor area | 향후 motor imagery 또는 robot control과 연결 가능 | posterior alpha, beta activity와 구분 필요 | Low-Medium |
| Gamma / 40 Hz activity | 고차 인지, binding, peak performance 후보 | task-specific, 해석 신중 | 장기 연구 후보로 남길 수 있음 | 근전도, 움직임, 장비 노이즈와 혼동 위험 큼 | Later |

## Key Points

### 1. Focus state는 직접 측정되는 대상이 아니라 조작적으로 정의해야 하는 상태다

EEG에서 직접 측정되는 것은 “집중” 자체가 아니라 시간에 따른 전위 변화, 주파수별 power, 동기성, 반응성 같은 신호 특성이다.

따라서 본 프로젝트에서는 focus state를 다음처럼 정의한다.

Focus state는 rest 또는 baseline condition과 비교했을 때, alpha suppression, low beta power increase, 또는 beta/alpha ratio increase와 같은 EEG feature 변화가 반복적으로 관찰되는 과제 수행 상태로 정의한다.

이 정의는 심리적 개념을 EEG feature와 혼동하지 않기 위한 것이다.

→ 집중은 EEG에서 직접 읽히는 값이 아니라, 조건 비교를 통해 추론되는 상태다.

### 2. Alpha reactivity는 초기 분석에서 가장 먼저 확인할 feature다

Alpha power는 정상 성인 EEG에서 비교적 안정적으로 관찰될 수 있고, eyes closed / eyes open 조건에 따라 반응성이 나타나기 쉽다.

특히 eyes closed 상태에서 posterior alpha activity가 증가하고, eyes open 또는 task condition에서 감소하는 alpha blocking / alpha suppression은 초기 분석에서 중요한 기준이 된다.

Alpha reactivity가 중요한 이유는 다음과 같다.

- 공개 EEG 데이터에서도 확인 가능한 경우가 많다.
- 실제 OpenBCI 측정 단계에서 장비와 전극 세팅을 확인하는 기준이 된다.
- rest와 active condition의 차이를 보기 쉽다.
- focus feature를 해석하기 전 baseline 반응성을 확인할 수 있다.

→ 초기 feature 선정에서 alpha power와 alpha suppression은 High priority로 둔다.

### 3. Low beta power는 focus-state 후보 feature로 검토할 수 있다

Low beta activity는 문제 해결, 계산, 외부 지향적 주의, task engagement와 관련된 후보 feature로 볼 수 있다.

다만 17 Hz 부근 activity가 주목할 만한 단서가 되더라도, 실제 분석에서는 단일 17 Hz amplitude를 곧바로 threshold로 사용하는 것은 적절하지 않다.

그 이유는 다음과 같다.

- 개인마다 beta peak frequency가 다를 수 있다.
- 특정 주파수의 amplitude는 preprocessing 방식에 따라 달라질 수 있다.
- 근전도, 긴장, 불안이 beta 대역에 영향을 줄 수 있다.
- 장비 특성이나 sampling rate에 따라 값이 흔들릴 수 있다.

따라서 현재 단계에서는 다음과 같이 band-level feature로 정의하는 것이 적절하다.

- low beta power = 14–20 Hz band power
- 또는 low beta power = 16–20 Hz band power
- low beta change = baseline 대비 task condition에서의 power 변화

→ Low beta는 focus-state 후보 feature로 남기되, 단일 주파수가 아니라 band power로 다룬다.

### 4. Beta / Alpha ratio는 threshold 제어로 연결하기 쉽지만, 과도한 단순화에 주의해야 한다

Beta / Alpha ratio는 alpha 감소와 beta 증가를 하나의 score로 결합할 수 있기 때문에, 향후 threshold 기반 제어에 연결하기 쉽다.

예를 들어 다음과 같은 방식으로 focus score를 정의할 수 있다.

focus_score = low_beta_power / alpha_power

이 값은 focus condition에서 alpha가 감소하고 low beta가 증가할 경우 상승할 가능성이 있다.

그러나 ratio feature는 단순한 만큼 해석상 위험도 있다.

- alpha가 감소하기만 해도 ratio가 증가할 수 있다.
- beta 증가가 근전도 artifact 때문이어도 ratio가 증가할 수 있다.
- 개인별 baseline 차이가 크다.
- rest/focus 분포가 실제로 분리되는지 확인해야 한다.

→ Beta / Alpha ratio는 초기 threshold 후보로 둘 수 있지만, 단독 feature로 확정하지는 않는다.

### 5. Theta와 Theta / Beta ratio는 보조 feature로 두는 것이 적절하다

Theta activity는 졸림, 이완, 정서, 작업기억, 주의 상태 등 다양한 맥락에서 설명된다.

이처럼 의미 범위가 넓기 때문에 theta power만으로 집중 상태를 해석하는 것은 위험하다.

Theta / Beta ratio 역시 attention-related index로 검토할 수 있지만, ADHD나 임상적 평가 맥락에서 자주 사용되는 지표이므로 일반적인 focus-state BCI에 그대로 적용할 때는 주의가 필요하다.

→ Theta 관련 feature는 주 feature가 아니라 보조 feature로 둔다.

### 6. SMR은 향후 robot control과 연결될 수 있지만, 현재 단계에서는 보조 후보로 둔다

SMR은 감각운동 영역과 관련된 rhythm으로, 향후 motor imagery나 robot control과 연결될 가능성이 있다.

특히 C3, Cz, C4 주변 sensorimotor area에서 관찰되는 SMR 변화는 이후 운동상상 기반 BCI를 다룰 때 중요해질 수 있다.

다만 현재 프로젝트의 3회차 목표는 focus-state feature 후보를 정리하는 것이므로, SMR은 즉시 사용할 핵심 feature라기보다 이후 robot control 단계에서 다시 검토할 후보로 둔다.

→ SMR은 장기적으로 중요하지만, 이번 단계에서는 alpha와 low beta보다 낮은 우선순위로 둔다.

### 7. Gamma / 40 Hz activity는 장기 후보로 남기되, 초기 feature에서는 보류한다

Gamma / 40 Hz activity는 고차 인지, 감각 정보 통합, binding, peak performance와 연결해 설명될 수 있는 후보 개념이다.

그러나 두피 EEG에서 30 Hz 이상의 activity는 근전도 artifact, 턱·이마 근육 긴장, 움직임, 장비 노이즈와 섞일 가능성이 크다.

현재 프로젝트의 다음 단계는 gamma 해석이 아니라 raw signal 구조 파악, artifact 구분, filtering, power spectrum 계산이다.

따라서 gamma는 현재 단계에서 핵심 feature로 채택하기보다, alpha와 low beta 분석이 안정화된 이후 검토할 장기 후보로 남기는 것이 적절하다.

→ Gamma / 40 Hz는 Later priority로 둔다.

## Initial Feature Priority

현재 단계에서의 feature 우선순위는 다음과 같다.

| Priority | Feature | Decision |
| --- | --- | --- |
| 1 | Alpha reactivity | 가장 먼저 확인한다 |
| 2 | Alpha suppression | rest/task 또는 baseline/task 차이를 보는 핵심 후보로 둔다 |
| 3 | Low beta power | focus 또는 problem-solving 후보 feature로 둔다 |
| 4 | Beta / Alpha ratio | threshold 기반 score 후보로 둔다 |
| 5 | Theta power, Theta / Beta ratio | 보조 feature로 둔다 |
| 6 | SMR power | 향후 motor imagery / robot control 단계에서 재검토한다 |
| 7 | Gamma / 40 Hz | 장기 후보로 보류한다 |

## Feature Selection Criteria

초기 feature 후보는 다음 기준에 따라 평가한다.

| Criterion | Meaning | Question |
| --- | --- | --- |
| Observability | 실제 EEG 데이터에서 관찰 가능한가 | raw signal과 power spectrum에서 확인되는가? |
| Reactivity | 조건 변화에 따라 변하는가 | eyes closed/open, rest/task 사이에서 달라지는가? |
| Repeatability | 반복 측정에서 유사한가 | trial 또는 subject 내에서 반복되는가? |
| Interpretability | 생리학적·신호처리적 의미를 설명할 수 있는가 | 왜 이 feature를 쓰는지 설명 가능한가? |
| Robustness | artifact와 구분 가능한가 | eye blink, EMG, movement와 구분되는가? |
| Simplicity | threshold 또는 classifier로 연결 가능한가 | 계산이 단순하고 실시간 처리 가능성이 있는가? |
| Stage suitability | 현재 프로젝트 단계에 맞는가 | 공개 EEG 데이터와 기초 preprocessing 단계에서 확인 가능한가? |

## Operational Definitions

초기 분석에서 사용할 수 있는 feature 정의는 다음과 같다.

### Alpha power

alpha_power = power(8–13 Hz)

주요 용도:

- eyes closed / eyes open 조건 비교
- posterior alpha 확인
- EEG 품질 및 상태 반응성 확인

### Alpha suppression

alpha_suppression = (alpha_baseline - alpha_task) / alpha_baseline

주요 용도:

- rest 대비 task 상태 변화 확인
- focus-state 후보 feature
- baseline reactivity 확인

### Low beta power

low_beta_power = power(14–20 Hz)

또는

low_beta_power = power(16–20 Hz)

주요 용도:

- 문제 해결, 계산, task engagement 후보 feature
- focus condition에서 증가 여부 확인

### Low beta change

low_beta_change = (low_beta_task - low_beta_baseline) / low_beta_baseline

주요 용도:

- absolute power보다 개인차를 줄인 비교
- 조건별 변화 확인

### Beta / Alpha ratio

beta_alpha_ratio = low_beta_power / alpha_power

주요 용도:

- focus score 후보
- threshold 기반 제어로 연결 가능

주의:

- alpha 감소만으로도 ratio가 증가할 수 있음
- beta 증가가 artifact일 경우 잘못된 trigger 발생 가능

## Interpretation Boundary

| Observation | Acceptable interpretation | Over-interpretation to avoid |
| --- | --- | --- |
| Alpha power decreased | 해당 조건에서 alpha band power가 감소했다 | 피험자가 반드시 집중했다 |
| Alpha suppression observed | baseline 대비 task condition에서 alpha 반응성이 나타났다 | 집중 상태가 직접 측정되었다 |
| Low beta increased | task condition에서 low beta power가 증가했다 | 문제 해결 능력이 향상되었다 |
| Beta / Alpha ratio increased | focus score 후보 값이 증가했다 | 의식 수준이 상승했다 |
| Theta / Beta ratio changed | attention-related 보조 지표가 변했다 | 주의력 상태가 확정적으로 진단되었다 |
| Gamma activity observed | high-frequency activity가 관찰되었다 | 고차 인지나 peak performance가 증명되었다 |
| Threshold crossed | feature value가 기준값을 넘었다 | 뇌의 의도 자체를 직접 읽었다 |

## Analysis Plan for Public EEG Data

다음 단계에서는 직접 피험자 실험이 아니라 공개 EEG 데이터를 활용해 raw signal과 feature 후보를 확인한다.

### Step 1. Dataset structure 확인

확인할 항목:

- file format
- sampling rate
- channel names
- reference 방식
- event marker
- condition label
- subject information
- recording duration

### Step 2. Raw signal 확인

확인할 항목:

- amplitude scale
- noisy channel
- sudden jump
- drift
- eye blink-like waveform
- muscle-like high-frequency noise
- line noise peak

### Step 3. Preprocessing 준비

초기 preprocessing 후보:

- band-pass filtering
- notch filtering if needed
- bad channel inspection
- epoch segmentation
- baseline correction 또는 normalization

### Step 4. Spectrum analysis

계산 후보:

- FFT
- power spectrum
- PSD
- band power
- relative band power

### Step 5. Feature extraction

우선 계산할 feature:

- alpha power
- alpha suppression
- low beta power
- low beta change
- beta / alpha ratio
- theta power
- theta / beta ratio

### Step 6. Condition comparison

조건이 있는 데이터라면 다음 비교를 우선한다.

- eyes closed vs eyes open
- rest vs task
- baseline vs stimulus
- low workload vs high workload

## Minimal Decision Rule Draft for Later Stage

아직 이번 단계에서 로봇 제어를 수행하지는 않는다.

하지만 향후 threshold 기반 제어로 연결하기 위해 다음과 같은 최소 decision rule을 생각할 수 있다.

if alpha_suppression > threshold_A  
and low_beta_change > threshold_B:  
    state = "focus_candidate"  
else:  
    state = "rest_or_uncertain"

또는 더 단순하게는 다음과 같이 시작할 수 있다.

focus_score = low_beta_power / alpha_power

if focus_score > subject_specific_threshold:  
    trigger = True  
else:  
    trigger = False

다만 이 rule은 실제 데이터에서 rest/focus feature distribution이 충분히 분리되는지 확인한 뒤에만 사용할 수 있다.

## Current Decision

현재 단계에서의 feature 선정 결론은 다음과 같다.

| Decision | Feature |
| --- | --- |
| Use first | Alpha reactivity |
| Main candidates | Alpha suppression, low beta power |
| Score candidate | Beta / Alpha ratio |
| Auxiliary candidates | Theta power, Theta / Beta ratio |
| Later candidate | SMR power |
| Defer | Gamma / 40 Hz activity |

## Summary

이번 feature list의 결론은 다음과 같다.

- Focus state는 직접 측정되는 대상이 아니라, 조건별 EEG feature 변화로 조작적으로 정의해야 한다.
- 초기 분석에서는 alpha reactivity와 alpha suppression을 가장 먼저 확인한다.
- Low beta power는 focus 또는 problem-solving condition의 후보 feature로 둔다.
- 17 Hz activity는 단일 threshold가 아니라 low beta band power로 다룬다.
- Beta / Alpha ratio는 threshold 기반 제어에 연결하기 쉽지만, 단독 feature로 확정하지 않는다.
- Theta와 SMR은 보조 후보로 두고, gamma / 40 Hz는 장기 후보로 보류한다.
- 다음 단계에서는 공개 EEG 데이터에서 raw signal, artifact, filtering, power spectrum을 먼저 확인한다.
