# EEG Frequency Bands and Rhythms

## Purpose

EEG의 주요 주파수 대역과 rhythm 개념을 정리하고, 각 대역을 BCI 관점에서 해석할 때의 기본 의미와 주의점을 구분한다.

이 문서는 EEG 신호의 전체 관찰 구조를 다루기보다, frequency band와 rhythm을 중심으로 정리한다.  
집중 상태 feature 선정은 별도 문서에서 다룬다.

## 1. Frequency Band vs Rhythm

EEG에서 frequency band와 rhythm은 같은 개념이 아니다.

Frequency band는 특정 주파수 범위에 속하는 EEG activity를 의미한다.  
반면 rhythm은 특정 주파수 범위뿐 아니라 위치, 파형, 규칙성, 반응성을 함께 갖는 반복적 활동이다.

| Concept | Meaning | Example |
| --- | --- | --- |
| Frequency band | 특정 주파수 범위에 속하는 EEG activity | 8–13 Hz alpha band |
| Rhythm | 주파수, 위치, 파형, 규칙성, 반응성을 갖는 반복 패턴 | posterior alpha rhythm |
| Activity | 특정 조건에서 관찰되는 EEG 변화 | beta activity during task |
| Background rhythm | 전체 EEG 기록에서 우세하게 나타나는 기본 리듬 | eyes-closed posterior alpha |

따라서 특정 주파수 activity가 보인다고 해서 곧바로 특정 rhythm으로 해석해서는 안 된다.

예를 들어 8–13 Hz activity가 관찰되더라도, 후두부 우세성, eyes closed 조건, eyes open 시 감소 같은 특징이 함께 확인되어야 alpha rhythm으로 해석할 수 있다.

## 2. Major EEG Frequency Bands

| Band / Rhythm | Frequency range | Main condition / context | BCI relevance | Main caution |
| --- | --- | --- | --- | --- |
| Delta | ~0.5–4 Hz | 깊은 수면, 느린 활동 | 초기 focus BCI에서는 주요 feature로 보기 어려움 | 눈 움직임, 움직임 artifact와 혼동 가능 |
| Theta | ~4–8 Hz | 졸림, 이완, 정서, 작업기억 등 | 보조 상태 지표로 검토 가능 | 의미 범위가 넓어 단독 해석 위험 |
| Alpha | ~8–13 Hz | awake, relaxed, eyes-closed 상태의 posterior rhythm | EEG 품질 확인, rest/active 조건 비교에 유용 | alpha band와 alpha rhythm 구분 필요 |
| SMR | ~12–15 Hz | sensorimotor area의 안정적 리듬 | 향후 motor imagery, robot control과 연결 가능 | posterior alpha, beta activity와 구분 필요 |
| Beta | ~13–30 Hz | 각성, 외부 지향적 주의, 문제 해결, 과제 수행 | focus 또는 task engagement 후보 대역 | EMG, 긴장, 불안과 혼동 가능 |
| Gamma | ~30–50 Hz 이상 | 고차 인지, 감각 통합, binding, peak performance 후보 | 장기 연구 후보 | artifact 위험이 커 초기 해석 주의 |

## 3. Band-specific Notes

### 1. Delta

Delta는 가장 느린 주파수 대역으로, 깊은 수면에서 두드러지게 나타난다.  
정상 성인의 각성 상태에서 뚜렷한 delta activity가 나타날 경우에는 신중한 해석이 필요하다.

BCI 관점에서 delta는 초기 focus-state feature로 사용하기보다는, 졸림, 움직임, 눈 움직임 artifact와 구분해야 할 대역으로 보는 것이 적절하다.

### 2. Theta

Theta는 졸림, 이완, 정서, 작업기억, 주의 상태 등 다양한 맥락에서 설명된다.  
의미 범위가 넓기 때문에 theta power 하나만으로 특정 상태를 단정하기 어렵다.

BCI에서는 주 feature라기보다 보조 feature로 검토할 수 있다.  
특히 focus condition을 해석할 때 theta 변화가 졸림 때문인지, 작업기억 부하 때문인지, 정서적 변화 때문인지 구분해야 한다.

### 3. Alpha

Alpha는 정상 성인 EEG에서 가장 기본적으로 확인할 수 있는 대역 중 하나다.  
일반적으로 awake, relaxed, eyes-closed 상태에서 후두부를 중심으로 나타난다.

눈을 뜨거나 시각 자극을 처리하거나 정신활동을 수행하면 alpha activity가 감소할 수 있다.  
이를 alpha blocking 또는 alpha suppression으로 볼 수 있다.

BCI 관점에서 alpha는 다음 이유로 중요하다.

- EEG 데이터 품질을 확인하는 기본 기준이 될 수 있다.
- eyes closed / eyes open 조건 비교에 적합하다.
- rest condition과 active condition의 차이를 확인하는 데 유용하다.
- focus-state feature를 설계하기 전 baseline reactivity를 확인할 수 있다.

단, alpha band power와 alpha rhythm은 구분해야 한다.  
8–13 Hz power가 있다고 해서 항상 정상적인 posterior alpha rhythm이 관찰된 것은 아니다.

### 4. SMR

SMR은 sensorimotor rhythm으로, 대체로 12–15 Hz 범위에서 감각운동 영역을 중심으로 관찰된다.  
주파수 범위는 alpha 또는 low beta와 겹칠 수 있지만, 위치와 반응성이 다르다.

SMR은 향후 motor imagery나 robot control 단계에서 중요해질 수 있다.  
다만 현재 단계에서는 focus-state feature의 중심이라기보다, 이후 운동 관련 BCI로 확장할 때 다시 검토할 rhythm으로 두는 것이 적절하다.

### 5. Beta

Beta activity는 일반적으로 각성, 외부 지향적 주의, 문제 해결, 과제 수행과 연결되어 설명된다.  
특히 low beta는 focus-state BCI에서 후보 대역으로 검토할 수 있다.

다만 beta activity는 근전도, 긴장, 불안, 움직임의 영향을 받을 수 있다.  
따라서 beta 증가를 곧바로 집중의 증거로 해석해서는 안 된다.

BCI 분석에서는 beta 전체를 하나로 보기보다, low beta와 high beta를 구분하는 것이 필요하다.

| Sub-band | Approximate range | Possible meaning | Caution |
| --- | --- | --- | --- |
| Low beta | ~14–20 Hz 또는 16–20 Hz | 문제 해결, 주의, task engagement 후보 | 단일 peak보다 band power로 보는 것이 적절 |
| High beta | ~20–30 Hz 이상 | 긴장, 고각성, 불안, 복잡한 처리 가능성 | EMG와 혼동 가능성 증가 |

### 6. Gamma

Gamma는 30 Hz 이상 대역의 빠른 activity로, 고차 인지, 감각 정보 통합, binding, peak performance와 관련해 설명된다.

그러나 두피 EEG에서 gamma 대역은 artifact 위험이 크다.  
근전도, 턱·이마 근육 긴장, 움직임, 장비 노이즈와 섞일 가능성이 높기 때문이다.

따라서 현재 단계에서는 gamma를 초기 feature로 사용하기보다, 장기적으로 검토할 후보 대역으로 남기는 것이 적절하다.

## 4. Rhythm-specific Interpretation

| Rhythm / Activity | Interpretation focus | What to check |
| --- | --- | --- |
| Alpha rhythm | posterior dominance, eyes-closed increase, eyes-open decrease | 위치, 반응성, baseline |
| SMR | sensorimotor area rhythm | C3, Cz, C4 주변 위치와 움직임 반응 |
| Beta activity | task-related activation candidate | EMG, 긴장, 조건별 변화 |
| Gamma activity | high-frequency candidate | artifact, muscle noise, 반복성 |

Rhythm을 해석할 때는 주파수 범위만 보지 않고, 위치와 반응성을 함께 확인해야 한다.

## 5. Interpretation Boundary

| Observation | Acceptable interpretation | Over-interpretation to avoid |
| --- | --- | --- |
| Alpha power decreased | 해당 조건에서 alpha band power가 감소했다 | 피험자가 반드시 집중했다 |
| Posterior alpha rhythm observed | alpha rhythm의 기본 조건 일부가 확인되었다 | 전체 인지 상태가 안정적이라고 단정 |
| Beta power increased | task condition에서 beta activity가 증가했다 | 문제 해결 능력이 향상되었다 |
| Gamma activity observed | high-frequency activity가 관찰되었다 | 고차 인지나 peak performance가 증명되었다 |
| Rhythm-like pattern observed | 반복적 EEG pattern이 나타났다 | 주파수만으로 기능적 rhythm이라고 단정 |

## 6. Link to Feature Selection

이 문서의 정리는 다음 단계의 feature selection으로 이어진다.

현재 단계에서 feature 후보로 연결될 수 있는 대역은 다음과 같다.

| Band / Rhythm | Link to feature selection |
| --- | --- |
| Alpha | alpha power, alpha suppression |
| Low beta | low beta power, low beta change |
| Beta / Alpha relation | beta/alpha ratio |
| Theta | theta power, theta/beta ratio as auxiliary feature |
| SMR | later motor imagery / robot control candidate |
| Gamma | later candidate, not initial threshold feature |

구체적인 feature 후보, 기대 변화, electrode, risk, initial priority는 별도 문서에서 정리한다.

## Summary

이번 문서의 핵심은 다음과 같다.

- Frequency band와 rhythm은 구분해야 한다.
- Alpha rhythm은 초기 EEG 분석에서 가장 먼저 확인할 수 있는 기준 rhythm이다.
- Beta activity는 focus-state 후보 대역이 될 수 있지만, EMG와 긴장 상태를 함께 고려해야 한다.
- SMR은 향후 motor imagery와 robot control 단계에서 다시 검토할 수 있다.
- Gamma/40 Hz는 장기 연구 후보로 남기되, 초기 threshold feature로 사용하기에는 artifact 위험이 크다.
- 대역별 의미는 feature selection의 출발점일 뿐, 특정 심리 상태의 직접 증거가 아니다.
