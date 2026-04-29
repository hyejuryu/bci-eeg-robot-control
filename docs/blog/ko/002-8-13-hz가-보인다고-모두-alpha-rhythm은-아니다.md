# 8–13 Hz가 보인다고 모두 alpha rhythm은 아니다

## English Medium Version

[Not Every 8–13 Hz Signal Is an Alpha Rhythm](MEDIUM_LINK)

## 작성 배경

이 글은 EEG-BCI 로봇 제어 프로젝트의 Session 03 기록을 바탕으로 작성한 두 번째 Medium 글이다.

첫 번째 글이 EEG 기반 BCI를 “뇌를 읽는 기술”이 아니라 `signal → feature → decision → control`의 pipeline으로 보는 글이었다면, 이 글은 그 다음 단계로 EEG feature를 해석할 때 필요한 기본적인 주의점을 다룬다.

특히 이번 글의 핵심은 **frequency band와 rhythm은 같은 것이 아니라는 점**이다.  
8–13 Hz 근처의 activity가 보인다고 해서 그것이 자동으로 의미 있는 alpha rhythm이 되는 것은 아니다. Alpha rhythm은 주파수뿐 아니라 위치, 상태, 반응성, 반복성, artifact 가능성까지 함께 고려해야 하는 생리적 패턴이다.

이 한국어 문서는 Medium에 발행할 영어 글의 companion note다. 기계적인 직역이 아니라, 영어 글의 의미와 문단 구조를 최대한 유지한 한국어 대응본으로 작성한다.

## 핵심 주장

EEG 분석에서 주파수 대역만 보고 심리 상태를 단정하면 위험하다.

Alpha rhythm은 단순히 8–13 Hz activity가 아니다.  
Alpha rhythm은 특정 주파수 범위뿐 아니라 scalp distribution, state dependency, reactivity, duration, artifact 가능성을 함께 고려해야 하는 구조화된 생리적 패턴이다.

따라서 초기 EEG-BCI 프로젝트에서는 곧바로 “focus”를 탐지하려 하기보다, 먼저 eyes-closed / eyes-open 조건에서 posterior alpha reactivity가 관찰되는지 확인하는 것이 더 적절하다.

## 본문 한국어 버전

처음 EEG를 공부하기 시작했을 때, 주파수 대역은 겉보기에는 단순해 보였다.

Delta는 느린 활동과 관련된다.  
Theta는 졸림이나 내적 처리와 자주 연결된다.  
Alpha는 흔히 이완으로 설명된다.  
Beta는 주의나 과제 몰입과 연결되는 경우가 많다.  
Gamma는 때때로 고차 인지와 관련된다고 설명된다.

이런 요약은 처음 지도를 그릴 때 유용하다.

하지만 동시에 오해를 낳을 수 있다.

만약 EEG 해석을 단순한 사전처럼 다룬다면 —

```text
alpha = relaxation
beta = concentration
gamma = higher cognition
```

— 나는 이미 문제에 빠진 것이다.

EEG 분석은 특정 주파수 범위를 찾고 거기에 심리적 라벨을 붙이는 일이 아니다. 8–13 Hz 근처의 신호가 보인다고 해서 그것이 자동으로 의미 있는 alpha rhythm이 되는 것은 아니다. Alpha power가 감소했다고 해서 누군가가 집중하고 있다는 뜻도 아니다. Beta power가 증가했다고 해서 주의집중이 증명되는 것도 아니다.

이 구분은 내가 진행 중인 EEG-BCI 프로젝트에서 중요하다. 나는 결국 EEG feature를 사용해 간단한 로봇 제어를 하고 싶기 때문이다.

어떤 feature가 로봇을 제어할 수 있는지 묻기 전에, 먼저 더 기본적인 질문을 해야 한다.

> 나는 정확히 무엇을 측정하고 있는가?

## Frequency band와 rhythm은 같은 것이 아니다

Frequency band는 범위다.

예를 들어 alpha band는 보통 8–13 Hz 근처의 활동으로 설명된다.

하지만 rhythm은 단순한 주파수 범위 이상이다.

Rhythm에는 구조가 있다. 맥락이 있다. 전형적인 분포, 상태 의존성, 지속 시간, 반응성, 그리고 다른 신호와의 관계가 있다.

즉, 특정 주파수 대역에서 power가 관찰되는 것만으로는 충분하지 않다. 그것이 어디에서 나타나는지, 어떤 조건에서 나타나는지, 반복되는지, 상태 변화에 반응하는지, artifact에 오염되었을 가능성은 없는지도 함께 보아야 한다.

다시 말하면 다음과 같다.

```text
frequency band = spectrum 안에서 activity가 나타나는 위치
rhythm = 맥락 안에서 해석되는 구조화된 생리적 패턴
```

이 차이는 작아 보일 수 있지만, EEG 데이터를 읽는 방식을 바꾼다.

주파수 대역만 본다면, 모든 10 Hz 성분을 alpha로 해석하고 싶어질 수 있다.

하지만 rhythm의 관점에서 생각하면, 그 10 Hz 활동이 alpha rhythm처럼 행동하는지 물어야 한다.

## 무엇이 alpha rhythm을 단순한 8–13 Hz 이상으로 만드는가?

Alpha rhythm은 단순히 8–13 Hz 사이의 모든 활동을 의미하지 않는다.

기본적인 EEG 맥락에서 alpha rhythm은 보통 깨어 있고, 이완되어 있으며, 눈을 감은 상태에서 더 분명하게 나타나는 posterior dominant rhythm으로 설명된다. 그리고 눈을 뜨거나 시각 처리 및 과제 몰입이 증가하면 감소하는 경향이 있다.

이 감소를 흔히 alpha blocking 또는 alpha suppression이라고 부른다.

따라서 중요한 질문은 이것만이 아니다.

> 8–13 Hz 근처의 activity가 있는가?

더 나은 질문은 이것이다.

> 이 activity가 예상되는 영역에서, 예상되는 조건 아래 나타나며, 상태 변화에 의미 있게 반응하는가?

예를 들어 초기 EEG 실험에서 나는 곧바로 “focus”를 탐지하려고 하지 않을 것이다.

더 나은 첫 단계는 다음을 비교하는 것이다.

```text
eyes closed
vs.
eyes open
```

만약 eyes-closed 구간에서 posterior alpha activity가 증가하고, eyes-open 상태에서 감소한다면, 이는 기록이 의미 있는 생리적 변화를 포착하고 있다는 기본적인 신호가 된다.

이것이 참가자가 깊은 심리적 의미에서 이완되어 있다는 것을 증명하지는 않는다.

단지 EEG 세팅이 기본적인 상태 의존적 반응을 감지하고 있을 가능성을 보여준다.

그것만으로도 이미 유용하다.

## BCI 제어 전에 alpha reactivity가 중요한 이유

초기 EEG-BCI 프로젝트에서 alpha reactivity는 단순한 뇌과학 개념이 아니다. 실용적인 점검 기준이다.

EEG로 무엇인가를 제어하기 전에, 내 세팅이 단순하고 예상 가능한 변화를 포착할 수 있는지 알아야 한다.

만약 eyes-closed와 eyes-open의 차이를 명확히 관찰할 수 없다면, focus 기반 로봇 제어로 서둘러 넘어가서는 안 된다.

그 대신 먼저 더 기본적인 문제들을 점검해야 한다.

- 전극 접촉
- reference 세팅
- channel 위치
- 눈 움직임 artifact
- 근전도 artifact
- 환경 노이즈
- filtering 선택
- preprocessing 오류

이런 의미에서 alpha reactivity는 sanity check다.

이것은 다음 질문에 답하는 데 도움이 된다.

> EEG 신호가 기본적인 생리적 조건 변화에 반응하고 있는가?

이 질문이 어느 정도 안정된 뒤에야 mental arithmetic, visual attention, focus task 같은 더 복잡한 조건으로 넘어가는 것이 좋다.

## Alpha suppression은 “집중”과 같은 말이 아니다

가장 쉬운 실수 중 하나는 이렇게 말하는 것이다.

> Alpha가 감소했으니 참가자가 집중했다.

어떤 실험 맥락에서는 가능할 수도 있지만, 일반적인 진술로는 너무 단순하다.

Alpha power는 여러 이유로 감소할 수 있다.

참가자가 눈을 떴을 수 있다.  
시각 입력을 처리하고 있을 수 있다.  
몸을 약간 움직였을 수 있다.  
전극 접촉이 변했을 수 있다.  
신호에 artifact가 포함되었을 수 있다.  
분석 window가 너무 짧거나 불안정할 수 있다.

따라서 alpha suppression만으로 집중의 직접적인 증거라고 해석해서는 안 된다.

더 조심스러운 표현은 다음과 같다.

> Baseline condition과 비교했을 때, task condition에서 alpha power가 감소했다.

더 나은 표현은 다음과 같다.

> Eyes-closed baseline과 비교했을 때, eyes-open 또는 task condition에서 posterior alpha power가 감소했으며, 이는 상태 의존적인 alpha reactivity를 시사한다.

이 표현은 덜 극적이다. 하지만 더 정확하다.

BCI에서는 극적인 해석보다 정확성이 더 중요하다.

## 이것이 focus 기반 BCI에 의미하는 것

내 프로젝트는 결국 EEG feature를 간단한 로봇 제어와 연결하는 것을 목표로 한다.

미래의 제어 로직은 이런 형태일 수 있다.

```python
if feature_value > threshold:
    send_command_to_robot()
```

하지만 이 로직은 feature가 잘 정의되어 있을 때에만 의미가 있다.

Focus를 너무 모호하게 정의하면, 제어 시스템은 시작하기도 전에 불안정해진다.

따라서 이렇게 말하는 대신,

```text
focus → beta increase → robot moves
```

더 조심스러운 실험 구조가 필요하다.

```text
defined baseline condition
→ defined task condition
→ feature extraction
→ distribution comparison
→ threshold decision
→ robot command
```

이것이 프로젝트 초기에 alpha reactivity가 중요한 이유다.

Alpha reactivity는 조건 변화가 측정 가능한 EEG feature와 어떻게 연결될 수 있는지 보여주는 첫 사례가 된다.

같은 논리는 이후 low beta power나 beta/alpha ratio 같은 더 어려운 feature에도 적용할 수 있다.

하지만 첫 단계를 건너뛰어서는 안 된다.

## 단순한 EEG 라벨의 문제

같은 주의는 다른 주파수 대역에도 적용된다.

Low beta activity는 주의, 과제 몰입, 문제 해결과 관련될 수 있다. 하지만 단일 beta 값을 보편적인 집중 지표처럼 다루어서는 안 된다.

Gamma activity, 특히 40 Hz 부근의 활동은 고차 인지, binding, peak performance와 관련해 자주 논의된다. 하지만 두피 EEG에서 고주파 활동은 근육 활동, 턱 긴장, 얼굴 움직임, 그리고 다른 artifact와 쉽게 섞일 수 있다.

즉, 주파수 라벨은 유용하지만 너무 빨리 사용하면 위험하다.

더 나은 접근은 주파수 대역을 결론이 아니라 feature candidate로 다루는 것이다.

```text
alpha band activity → candidate feature
low beta power → candidate feature
gamma activity → later candidate, only after artifact control
```

목표는 모든 주파수 대역에 정신 상태를 배정하는 것이 아니다.

목표는 어떤 feature가 정의된 실험 조건 아래에서 안정적으로 행동하는지 테스트하는 것이다.

## 초기 EEG 분석을 위한 실용적인 체크리스트

현재 프로젝트에서 나는 EEG를 너무 빨리 해석하는 것을 피하고 싶다.

어떤 것을 의미 있는 feature라고 부르기 전에, 다음을 물어야 한다.

1. 어떤 frequency band를 측정하고 있는가?
2. 어떤 channel 또는 scalp region에서 나온 신호인가?
3. 참가자는 어떤 condition에 있었는가?
4. 참가자의 eye state는 통제되었는가?
5. 그 pattern은 trial 간에 반복되는가?
6. 그 signal은 artifact로 설명될 수 있는가?
7. 그 feature는 baseline과 비교되었는가?
8. 그 distribution은 threshold 기반 제어에 사용할 만큼 충분히 분리되는가?

이 체크리스트는 단순하지만, 흔한 실수를 막아준다.

> EEG band를 mental state의 직접적인 라벨처럼 다루는 것.

그 실수는 더 흥미로운 이야기를 만들어낼 수 있다.

하지만 더 약한 실험을 만든다.

## 현재 프로젝트에서 alpha의 역할

현재 단계에서 alpha는 나의 최종 BCI feature가 아니다.

Alpha는 pipeline이 작동하는지 확인하는 첫 번째 테스트다.

즉각적인 목표는 내가 focus를 탐지할 수 있음을 증명하는 것이 아니다.

즉각적인 목표는 다음과 같은 기본 EEG 반응을 관찰할 수 있는지 확인하는 것이다.

```text
eyes closed → posterior alpha increase
eyes open   → alpha suppression
```

이 기본 반응이 보인다면, 그다음 더 복잡한 분석으로 넘어갈 수 있다.

- task condition에서의 alpha suppression
- problem-solving task에서의 low beta power
- beta/alpha ratio
- baseline-normalized feature changes
- feature distribution을 바탕으로 한 threshold design

이 순서는 중요하다.

BCI 시스템은 극적인 주장으로 시작해서는 안 된다.

측정 가능한 차이에서 시작해야 한다.

## 결론

8–13 Hz 신호가 보인다고 모두 alpha rhythm은 아니다.

모든 alpha 감소가 focus를 의미하지는 않는다.

모든 beta 증가가 attention을 의미하지도 않는다.

그리고 모든 주파수 대역을 심리적 라벨로 바꾸어서는 안 된다.

EEG 기반 BCI에서 중요한 질문은 단순히 이것이 아니다.

> 어떤 frequency band가 변했는가?

더 나은 질문은 이것이다.

> 어떤 condition에서 변했는가, 어디에서 나타났는가, 얼마나 안정적이었는가, 그리고 신뢰할 수 있는 decision rule을 지지할 수 있는가?

이런 질문이 있어야 EEG 분석에서 로봇 제어로 넘어갈 수 있다.

목표는 EEG를 신비롭게 보이게 만드는 것이 아니다.

목표는 EEG를 사용할 수 있게 만드는 것이다.

---

## 추가 메모

- 이 글은 프로젝트의 두 번째 외부 공개 글로 기획되었다.
- 첫 번째 글이 EEG-BCI 전체 pipeline을 설명했다면, 이 글은 EEG feature 해석의 첫 번째 주의점인 `frequency band ≠ rhythm`을 다룬다.
- 핵심은 “alpha = relaxation”, “beta = concentration” 같은 단순 대응을 피하는 것이다.
- 프로젝트 관점에서 alpha는 최종 BCI feature라기보다, OpenBCI 측정 전후로 pipeline이 정상적으로 작동하는지 확인하는 첫 번째 sanity check에 가깝다.
- 이후 별도 글로 확장할 수 있는 주제는 다음과 같다.
  - EEG에서 alpha reactivity를 확인하는 실험 설계
  - Focus condition을 EEG 실험으로 조작적으로 정의하는 방법
  - Low beta power를 focus feature로 사용할 때의 한계
  - Gamma / 40 Hz activity를 초기에 쓰기 어려운 이유

## 관련 Session 기록

- [Session 03](../../../weekly-notes/session-03-260425.md)

## 관련 Blog Archive

- [001. EEG는 뇌를 읽는 기술이 아니다](./001-eeg는-뇌를-읽는-기술이-아니다.md)
- [English version](../en/002-not-every-8-13-hz-signal-is-an-alpha-rhythm.md)

## References

- 전경희, 원희욱, 정문주, 전병현, 강형원. *뇌파와 뉴로피드백의 이해*. 아카데미아, 2023.
- 대한뇌파연구회. *뇌파분석의 기법과 응용*. 대한의학, 2023.
