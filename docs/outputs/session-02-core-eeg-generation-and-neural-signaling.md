## Purpose
EEG 신호가 어떤 신경생리학적 과정에서 발생하는지 이해하고,
BCI에서 해석 가능한 신호 수준과 한계를 구분한다.

## Core Structure
| Domain                | Key components                    | What actually happens                              | Why it matters for EEG/BCI |
| --------------------- | --------------------------------- | -------------------------------------------------- | -------------------------- |
| Neural signal origin  | Neuron, dendrite, axon, synapse   | 외부/내부 자극 → 전기적 신호 생성 및 전달                          | EEG는 이 과정의 간접 결과           |
| Membrane potential    | Ion channels (Na+, K+, Ca2+, Cl-) | 이온 이동 → 전위 변화 (depolarization / hyperpolarization) | 신호 생성의 물리적 기반              |
| Local potential       | EPSP / IPSP                       | 연접후 전위가 시간·공간적으로 누적됨                               | EEG의 주요 구성 요소              |
| Action potential      | Threshold-based spike             | 축삭둔덕에서 threshold 넘으면 발생                            | EEG에서는 직접적으로 거의 관측되지 않음    |
| Synaptic transmission | Neurotransmitter release          | 화학적 전달 → 연접후막 전위 변화                                | EEG 신호의 핵심 발생 원인           |
| Population activity   | Synchronization of neurons        | 다수 뉴런이 동기화될 때 전기장 형성                               | EEG 측정 가능 조건               |
| EEG signal formation  | Field potential (dipole)          | 연접후전위의 합 → scalp에서 측정                              | 우리가 실제로 사용하는 신호            |

## Key Points
### 1. EEG는 “스파이크”가 아니라 “연접후전위의 집단 합”이다
단일 뉴런의 활동전위는 EEG에 거의 반영되지 않음
주된 신호는 dendrite에서 발생하는 postsynaptic potential의 합

→ EEG = low-resolution population signal

### 2. “동기화”가 측정 가능성의 핵심 조건이다
뉴런이 많이 활성화되는 것만으로는 부족
같은 방향, 같은 타이밍으로 정렬된 활동이 필요

→ synchronization이 깨지면 신호는 noise처럼 보임

### 3. EEG는 위치도, 원인도 직접적으로 알려주지 않는다
측정되는 전위는 여러 source의 선형 합
전극 아래 정확한 위치를 의미하지 않음

→ 해석은 항상 “간접적”이다

### 4. 신경전달물질은 직접 측정 대상이 아니라 “상태 조절 변수”다
도파민, 노르에피네프린, 세로토닌 등은
→ attention, arousal, motivation 조절

→ EEG에서는 결과 패턴 변화로만 나타남

### 5. 신경가소성은 “시간 축”에서의 변화 개념이다
반복 자극 → 연접 강도 변화 (LTP/LTD)
구조적/기능적 재구성

→ 단일 실험보다
→ 훈련, 반복, 조건 변화 실험에서 의미 있음

## Interpretation Boundary (중요)
| Level            | What we can observe | What we cannot directly observe     |
| ---------------- | ------------------- | ----------------------------------- |
| Neuron level     | ❌                   | spike timing, membrane threshold    |
| Synapse level    | ❌                   | neurotransmitter dynamics           |
| Population level | ⭕                   | oscillation, power, synchronization |
| Behavioral level | ⭕ (indirect)        | attention, intention (추론 가능)        |

## Implication for BCI
- 우리는 neuron을 제어하는 게 아니라
→ population signal pattern을 이용하는 것

- 따라서 목표는:
  feature extraction 가능한 신호 정의
  안정적인 state difference 확보
