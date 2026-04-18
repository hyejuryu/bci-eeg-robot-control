## Purpose
EEG 신호를 구성하는 요소를 정리하고,
이를 BCI feature 및 실험 설계로 연결한다.

## EEG Signal Components
| Component    | Description | Practical meaning      |
| ------------ | ----------- | ---------------------- |
| Amplitude    | 전위 크기       | 신호 강도 (개인 baseline 중요) |
| Frequency    | 1초당 진동 수    | 상태 구분의 핵심              |
| Waveform     | 파형 형태       | 특정 패턴 식별 가능            |
| Synchrony    | 동기화 정도      | 기능적 연결성 힌트             |
| Distribution | 공간적 분포      | 영역별 활성 추정              |
| Phase        | 위상 관계       | 연결 및 타이밍 분석            |

## Frequency Bands (BCI 관점)
| Band  | Range     | Typical interpretation | BCI relevance |
| ----- | --------- | ---------------------- | ------------- |
| Delta | ~0.5–4 Hz | 깊은 수면                  | 거의 사용 안함      |
| Theta | ~4–8 Hz   | 기억, 내부 처리              | 보조 feature    |
| Alpha | ~8–13 Hz  | 안정, 휴식 (↓ = 집중)        | 핵심 feature    |
| Beta  | ~13–30 Hz | 집중, 인지 활동              | 핵심 feature    |
| Gamma | 30+ Hz    | 고차 인지                  | 실험 난이도 높음     |

## ERP (Event-Related Potential)
| Component | Meaning   | Experimental use |
| --------- | --------- | ---------------- |
| P50       | 감각 gating | 정보 억제 능력         |
| N170      | 얼굴 인식     | 시각 자극 처리         |
| P300      | 목표 자극 인식  | BCI에서 매우 중요      |
| MRCP      | 운동 준비 신호  | motor-based BCI  |

## Two Experimental Directions
### 1. Continuous state-based approach
- rest vs focus
- alpha/beta power 비교
- threshold 기반 제어
→ 장점: 구현 쉬움
→ 단점: 신호 불안정

### 2. Event-based (ERP) approach
- oddball paradigm
- target stimulus detection
- P300 기반 제어
→ 장점: 명확한 signal
→ 단점: 실험 설계 필요

## Feature Candidates (초기 BCI용)
| Feature                  | Description  | Complexity |
| ------------------------ | ------------ | ---------- |
| Band power (alpha, beta) | 가장 기본        | 낮음         |
| Band ratio               | beta/alpha 등 | 낮음         |
| Moving average power     | window 기반    | 낮음         |
| Threshold crossing       | 제어 신호        | 낮음         |
| ERP amplitude (P300)     | 자극 기반        | 중간         |
| Coherence                | 연결성          | 높음         |

## Signal Processing Pipeline (Revisited)
Raw EEG
→ filtering (band-pass)
→ artifact removal
→ segmentation (window)
→ FFT / power calculation
→ feature selection
→ threshold decision

## Noise vs Signal (중요 포인트)
| Type                      | Example             | Handling |
| ------------------------- | ------------------- | -------- |
| Artifact (제거 대상)          | 눈깜빡임, 근전도           | 제거       |
| Physiological variability | 개인차, 집중 fluctuation | 유지       |
| Environmental noise       | 전기 잡음               | 필터링      |

→ 핵심: 모든 noise를 제거하는 게 아니라, 의미 있는 변동성과 제거할 artifact를 구분하는 것

## Bridge to Next Session
### 개념 단계 — 3회차
- alpha / beta / theta / gamma 대역 의미 정리
- 각 대역이 attention / rest 상태와 어떻게 연결되는지 정리
- 초기 BCI feature 후보 (alpha, beta 등) 선정

### 실습 준비 — 5~6회차
- Python 환경 구성
- EEG 데이터 구조 (sampling rate, channel) 이해

### 실습 — 7회차 이후
- band-pass filtering
- FFT 직접 실행
- band power 계산 및 시각화
- rest vs focus 차이 확인

## Key Insight
- BCI에서 중요한 것은:
“신경생리학적으로 정확한 설명”이 아니라
“반복 가능하고 분리 가능한 신호 패턴”

## Final Summary 
- EEG는 복잡한 생리학적 과정의 결과지만
- BCI에서는 이를 단순한 feature로 축소해야 한다
- 따라서 핵심은:
→ 해석 가능한 feature 선택
→ 안정적인 실험 조건 설계
