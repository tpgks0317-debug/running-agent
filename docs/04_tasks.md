# Tasks

Do ONE task at a time. After each task: run tests, try the scenario, and make sure you understand the code.

Prompt for your AI assistant:
> Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.

## Part 1 — Foundation (재사용 — 카페 에이전트와 동일, 수정 없음)
- [x] **1. Config & LLM client.** `src/config.py`, `src/llm_client.py` — 그대로 재사용.
- [x] **2. Data store.** `src/tools/data_store.py` — 그대로 재사용.

## Part 2 — First tool & the agent loop
- [x] **3. get_profile.** `profile_tools.py`에 구현, `tools/__init__.py`에 등록. Check: `pytest -k get_profile`.
- [x] **4. Agent loop.** `src/agent.py`, `src/main.py` — 그대로 재사용.

## Part 3 — Many tools
- [x] **5. set_profile + calculate.** Check: `pytest -k "profile or calculate"`.
- [x] **6. get_goal + set_goal.** Check: `pytest -k goal`, Scenario A/C.
- [x] **7. get_courses.** Check: `pytest -k course`, Scenario A.
- [x] **8. log_run + get_progress_report.** Check: `pytest -k run`, Scenario B/D.
- [x] **9. Make the agent visible.** `agent.py`의 도구 호출 로그 출력 — 그대로 재사용.

## Part 4 — Context engineering
- [x] **10. Robustness.** Scenario E (잘못된 난이도/목표 미설정)로 오류 회복 확인.
- [x] **11. History trimming.** `MAX_HISTORY_MESSAGES` 트리밍 — 그대로 재사용. Check: Scenario F.

## Part 5 — Your own tool
- [x] **12. Design generate_training_plan.** `docs/03_tool_spec.md`에 명세 작성 완료.
- [x] **13. Build it.** `generate_training_plan` 구현, 등록, 테스트. 대표 시나리오: "10km를 50분 안에 뛰고 싶어. 코스 추천하고 훈련 계획도 짜줘."

## Part 6 — Real map data
- [x] **14. plan_route (map API).** `route_tools.py` — 실제 지도 데이터로 출발지 기준 순환 코스 생성. Check: `pytest -k plan_route`, Scenario G.
