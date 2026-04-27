# EEG Frequency Bands and Rhythms

## Purpose

EEG 신호의 주요 주파수 대역과 rhythm 개념을 정리하기 전, EEG 신호의 기본적 특성과 EEG 신호 파악의 주의점을 학습한다.

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
