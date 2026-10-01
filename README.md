# 🏃 Running Coach Agent

An AI assistant for a single runner training toward a personal goal — it uses **tools**
(profile, goal, local course list, run log, weekly training plan generator) to answer
questions and take actions on local JSON data.

Example: "10km를 50분 안에 뛰고 싶어. 코스 추천하고, 주 3번 훈련 계획도 짜줘."

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your API key in .env
```

## Run
```bash
python -m src.main               # chat with the agent (CLI)
python -m src.web                # chat with the agent (web UI, http://127.0.0.1:5000)
python -m pytest tests           # test tools (no LLM needed)
```

In the web UI, a route made by `plan_route` is drawn on a map under the answer.
The web server is a Python (Flask) app, so GitHub stores the code but cannot run it — to put it
online, use a Python host (it reads `HOST` / `PORT` from the environment) and set `API_KEY`,
`BASE_URL`, `MODEL` there. Never commit `.env`.

> **Windows note:** `agent.py` logs each tool call with an emoji (🔧). If your console
> codepage isn't UTF-8 (default on Korean Windows: cp949), it can crash with
> `UnicodeEncodeError` on the first tool call. Fix by setting UTF-8 I/O before running:
> `set PYTHONUTF8=1` (cmd) or `$env:PYTHONUTF8=1` (PowerShell).

## How to work on this project (vibe coding)
1. Open `docs/04_tasks.md` and pick the next unchecked task.
2. Ask your AI coding assistant:
   > Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.
3. Verify: run the tests and try the matching prompt in `tests/scenarios.md`.
4. Understand the code before moving on. You will be asked to explain it.

## Where is the "context"?
| For the coding assistant | For the agent (runtime) |
|---|---|
| `AGENTS.md`, `docs/` | `prompts/system_prompt.md`, tool descriptions, tool results, message history |

## Tools
| Tool | Type | What it does |
|---|---|---|
| `get_profile` | read | Height, weight, age, recent pace, usual distance |
| `set_profile` | write | Update body stats / running ability (confirm first) |
| `get_goal` | read | Current goal (distance, time, target pace, target date) |
| `set_goal` | write | Set a distance-within-time goal (confirm first) |
| `get_courses` | read | Local course list filtered by difficulty/region (stands in for a map API) |
| `plan_route` | read | Real loop route from a start place and distance, via free map APIs (measured distance, climb, difficulty) |
| `log_run` | write | Record a run's distance/time (confirm first) |
| `get_progress_report` | read | Total runs, distance, average pace, last run date |
| `generate_training_plan` | read | Weekly training schedule toward the goal, by days/week |
| `calculate` | compute | Arithmetic, e.g. comparing paces |

Built from the café-agent skeleton (same `config.py` / `llm_client.py` / `agent.py` / `main.py` / `data_store.py`), with the domain swapped for a personal running coach.
