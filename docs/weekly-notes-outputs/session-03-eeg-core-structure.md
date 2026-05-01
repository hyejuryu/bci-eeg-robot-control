# EEG Core Structure
Related study note: [Session 03](../../weekly-notes/session-03-260425.md)

## Purpose

EEG 신호의 주요 주파수 대역과 rhythm 개념을 정리하기 전, EEG 신호를 해석할 때 필요한 기본 관찰 요소와 주의점을 정리한다.

이 문서의 목적은 EEG를 단일 주파수 값이 아니라, 시간적·공간적·상태 의존적 패턴으로 이해하기 위한 기본 구조를 세우는 것이다.

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

### 2. Wave, rhythm, background activity는 구분해야 한다

EEG에서 하나의 wave는 특정 시점에 관찰되는 전위 변화다.  
반면 rhythm은 일정한 주파수 범위뿐 아니라 위치, 파형, 규칙성, 반응성을 갖는 반복적 활동이다.  
Background activity는 전체 기록에서 관찰되는 EEG 활동의 총체적 패턴이다.

따라서 특정 주파수 범위의 activity가 보인다고 해서 곧바로 기능적 rhythm으로 해석해서는 안 된다.

| Concept | Meaning |
| --- | --- |
| Wave | 한 채널에서 시간에 따라 관찰되는 전위 변화 |
| Rhythm | 특정 주파수, 위치, 형태, 규칙성, 반응성을 갖는 반복적 활동 |
| Background activity | 전체 기록에서 나타나는 EEG 활동의 총체적 패턴 |
| Frequency band | 특정 주파수 범위에 속하는 activity |

이 구분은 이후 alpha band와 alpha rhythm, beta activity와 SMR, gamma activity를 해석할 때 중요하다.

### 3. Reactivity는 EEG feature 해석의 핵심 조건이다

EEG feature는 절대값만으로 해석하기 어렵다.  
중요한 것은 특정 조건 변화에 따라 신호가 반복적으로 달라지는지 여부다.

예를 들어 정상 성인에서 eyes closed 상태의 posterior alpha activity는 eyes open 또는 task condition에서 감소할 수 있다.  
이러한 alpha blocking 또는 alpha suppression은 EEG가 상태 변화에 반응하는지를 확인하는 대표적인 예시다.

BCI 관점에서 reactivity가 중요한 이유는 다음과 같다.

- rest condition과 active condition을 구분할 수 있다.
- feature가 실제 상태 변화에 반응하는지 확인할 수 있다.
- threshold 또는 classifier에 사용할 후보 feature를 좁힐 수 있다.
- 장비나 전극 세팅이 정상적으로 작동하는지 확인하는 기준이 될 수 있다.

따라서 초기 EEG 분석에서는 feature 값을 바로 해석하기보다, 조건 변화에 따른 반응성을 먼저 확인하는 것이 적절하다.

### 4. Baseline과 condition을 구분해야 한다

EEG는 개인차, 전극 상태, 피로도, 각성 수준, 시각 조건, 움직임 등에 따라 쉽게 달라진다.  
따라서 특정 feature의 절대값만으로 상태를 판단하기 어렵다.

BCI feature를 해석하려면 다음 구분이 필요하다.

| Term | Meaning |
| --- | --- |
| Baseline | 비교 기준이 되는 안정 상태 또는 초기 상태 |
| Condition | eyes open, eyes closed, rest, task 등 실험 조건 |
| Change | baseline과 condition 사이에서 나타나는 feature 변화 |
| Pattern | 여러 trial 또는 반복 측정에서 재현되는 변화 방향 |

따라서 초기 분석에서는 absolute power보다 baseline 대비 변화, 조건별 차이, 반복 가능성을 함께 보는 것이 중요하다.

### 5. Artifact 확인은 feature extraction 이전 단계다

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

따라서 공개 EEG 데이터나 OpenBCI 데이터를 분석할 때는 feature extraction보다 raw signal과 artifact 확인이 먼저다.

## Interpretation Boundary

| Level | What can be observed | What should not be over-interpreted |
| --- | --- | --- |
| Raw EEG | 시간에 따른 전위 변화 | 특정 생각이나 의도 자체 |
| Frequency band | 특정 주파수 범위의 power 변화 | 특정 심리 상태의 직접 증거 |
| Rhythm | 위치, 형태, 반응성을 가진 반복 패턴 | 주파수만으로 rhythm이라고 단정 |
| Reactivity | 조건 변화에 따른 신호 변화 | 상태의 원인을 직접 증명 |
| Feature | 계산 가능한 수치적 패턴 | 집중, 의식, 창의성 자체 |
| BCI decision | threshold 또는 classifier output | 뇌의 의도를 직접 읽은 결과 |

## Implication for Later Analysis

이 문서를 바탕으로 이후 분석에서는 다음 순서를 따른다.

1. raw EEG signal의 기본 구조를 확인한다.
2. channel, sampling rate, reference, amplitude scale을 확인한다.
3. artifact와 noisy channel을 먼저 확인한다.
4. frequency band와 rhythm을 구분한다.
5. baseline과 condition을 나누어 feature 변화를 본다.
6. alpha, low beta, beta/alpha ratio 등 후보 feature를 계산한다.
7. feature 분포가 조건별로 충분히 구분되는지 확인한 뒤 threshold 또는 classifier를 검토한다.

## Summary

EEG는 단일 주파수 값으로 해석할 수 있는 신호가 아니다.  
파형, 진폭, 주파수, 분포, 위상관계, 동기성, 지속성, 반응성, artifact를 함께 고려해야 한다.

현재 단계에서 중요한 결론은 다음과 같다.

- EEG feature는 단일 값보다 조건별 변화 pattern으로 봐야 한다.
- Wave, rhythm, background activity, frequency band는 구분해야 한다.
- Reactivity는 BCI feature 후보를 선정할 때 핵심 기준이다.
- Baseline과 condition의 차이를 보지 않으면 feature 해석이 불안정하다.
- Artifact 확인은 feature extraction 이전에 수행해야 한다.
