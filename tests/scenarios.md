# Test Scenarios

Run `python -m src.main` and type each prompt. Compare the tool calls with the expected ones.
The exact order may vary slightly; what matters is that the agent uses tools instead of guessing.

| # | Prompt | Expected tool calls | What to check |
|---|---|---|---|
| A | 10km를 50분 안에 뛰는 게 목표야. 청주에서 평지 코스 추천해주고, 지금 내 페이스랑 목표 페이스 차이도 알려줘. | (확인 요청) → `set_goal` → `get_courses` → `get_profile` → `calculate` | 평지 코스 2곳 제시, 목표 페이스 5.0분/km vs 현재 7.2분/km 차이 계산 |
| B | 오늘 5km를 32분에 뛰었어. 기록해 줘. | (확인 요청) → `log_run` | "예" 확인 뒤에만 기록되고 페이스(6.4분/km)가 계산됨 |
| C | 내 목표가 뭐였지? | `get_goal` | 목표가 없으면 안내, 있으면 거리/시간/목표 페이스 보여줌 |
| D | 지금까지 얼마나 뛰었어? | `get_progress_report` | 총 러닝 횟수, 총 거리, 평균 페이스 요약 |
| E | 산악 코스로 추천해줘. (존재하지 않는 난이도) | `get_courses` → error → 다시 질문하거나 `get_courses` 재호출 | 회복하고 유효한 난이도(평지/완만한 언덕/언덕 많음) 안내 |
| F | 대화를 15턴 이상 나눈 뒤 "내가 처음에 뭐라고 물었지?" | — | 죽지 않음. 트리밍 후 에이전트가 처음 질문을 잊는지 관찰 |
| G | 무심천 체육공원에서 출발하는 5km 코스 짜줘. | `plan_route(start, distance_km=5)` | 실제 거리(약 5km)·누적 상승·난이도·주요 도로를 도구 결과 그대로 답함. `data/route.json` 생성됨 |

> A 테스트 전 목표가 없으면 정상, 있으면 먼저 `data/goal.json`을 `{}`로 되돌린다.
> B 테스트 후 데이터 초기화: `data/runs.json`의 `records`를 `[]`로 되돌린다.

## My scenario (대표 질문 — generate_training_plan)
| Prompt | Expected tool calls | What to check |
|---|---|---|
| 10km를 50분 안에 뛰고 싶어. 코스 추천하고, 주 3번 훈련 계획도 짜줘. | (확인 요청) → `set_goal` → `get_courses` → `generate_training_plan(days_per_week=3)` | 목표 확인 후 저장, 코스 추천, 월/수/금 식으로 3일 훈련 계획(조깅→페이스훈련→장거리) 생성 |
