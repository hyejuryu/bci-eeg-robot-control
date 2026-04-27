# Focus-State Feature List and Selection Criteria

## Purpose

집중 상태 기반 BCI에서 사용할 수 있는 EEG feature 후보를 정리하고, 각 feature의 기대 변화, 사용 가능성, 한계, 초기 우선순위를 구분한다.

이 문서의 목적은 “집중”을 직접 측정한다고 가정하는 것이 아니라, rest 또는 baseline condition과 비교했을 때 반복적으로 관찰 가능한 EEG feature 변화를 정리하는 것이다.

## Focus State Definition

본 프로젝트에서 focus state는 다음과 같이 조작적으로 정의한다.

Focus state는 rest 또는 baseline condition과 비교했을 때, alpha suppression, low beta power increase, beta/alpha ratio increase와 같은 EEG feature 변화가 반복적으로 관찰되는 과제 수행 상태로 정의한다.

즉, 집중은 EEG에서 직접 읽히는 값이 아니라, 조건 비교를 통해 추론되는 상태다.

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

| Feature | Operational definition | Main use |
| --- | --- | --- |
| Alpha power | power(8–13 Hz) | eyes closed / eyes open 조건 비교, EEG 품질 확인 |
| Alpha suppression | (alpha_baseline - alpha_task) / alpha_baseline | baseline 대비 task 상태 변화 확인 |
| Low beta power | power(14–20 Hz) 또는 power(16–20 Hz) | 문제 해결, 계산, task engagement 후보 feature |
| Low beta change | (low_beta_task - low_beta_baseline) / low_beta_baseline | baseline 대비 low beta 변화 확인 |
| Beta / Alpha ratio | low_beta_power / alpha_power | focus score 및 threshold 후보 |
| Theta / Beta ratio | theta_power / beta_power | attention-related 보조 지표 |

## Initial Decision

현재 단계에서 feature 선정 결론은 다음과 같다.

| Decision | Feature |
| --- | --- |
| Use first | Alpha reactivity |
| Main candidates | Alpha suppression, low beta power |
| Score candidate | Beta / Alpha ratio |
| Auxiliary candidates | Theta power, Theta / Beta ratio |
| Later candidate | SMR power |
| Defer | Gamma / 40 Hz activity |

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

## Link to Next Session

다음 단계에서는 직접 피험자 실험이 아니라 공개 EEG 데이터를 활용해 raw signal과 feature 후보를 확인한다.

우선 확인할 항목은 다음과 같다.

- dataset file format
- sampling rate
- channel names
- reference 방식
- event marker 또는 condition label
- raw signal amplitude scale
- noisy channel 여부
- eye blink, eye movement, EMG artifact
- band-pass filtering 전후 waveform 변화
- power spectrum 또는 PSD
- alpha power, low beta power, beta/alpha ratio의 조건별 변화

## Summary

이번 feature list의 결론은 다음과 같다.

- Focus state는 직접 측정되는 대상이 아니라, 조건별 EEG feature 변화로 조작적으로 정의해야 한다.
- 초기 분석에서는 alpha reactivity와 alpha suppression을 가장 먼저 확인한다.
- Low beta power는 focus 또는 problem-solving condition의 후보 feature로 둔다.
- 17 Hz activity는 단일 threshold가 아니라 low beta band power로 다룬다.
- Beta / Alpha ratio는 threshold 기반 제어에 연결하기 쉽지만, 단독 feature로 확정하지 않는다.
- Theta와 SMR은 보조 후보로 두고, gamma / 40 Hz는 장기 후보로 보류한다.
- 다음 단계에서는 공개 EEG 데이터에서 raw signal, artifact, filtering, power spectrum을 먼저 확인한다.
