# Tool Specifications

Write the spec BEFORE implementing a tool. The "Purpose" line becomes the tool description the LLM reads.

## Template
```
## Tool: <name>
- File: src/tools/<file>.py
- Purpose: <one clear sentence — this is what the LLM sees>
- Type: read | write | compute
- Parameters: <name> (<type>, required|optional) — <description>
- Returns: <example JSON>
- Errors: <when> → <example error JSON with a hint>
- Example request: "<a user sentence that should trigger this tool>"
```

---

## Tool: get_profile
- File: src/tools/profile_tools.py
- Purpose: Get the user's body stats and current running ability (height, weight, age, recent pace, usual distance).
- Type: read
- Parameters: none
- Returns: `{"height_cm": 170, "weight_kg": 68, "age": 32, "recent_pace_min_per_km": 7.2, "usual_distance_km": 3.0}`
- Errors: none — a profile always exists (pre-filled with defaults, update with set_profile)
- Example request: "내 프로필 좀 보여줘."

## Tool: set_profile
- File: src/tools/profile_tools.py
- Purpose: Update the user's body stats and current running ability. Only call after the user confirms.
- Type: write
- Parameters: height_cm (number, required); weight_kg (number, required); age (integer, required); recent_pace_min_per_km (number, required) — minutes per km; usual_distance_km (number, required)
- Returns: `{"height_cm": 170, "weight_kg": 68, "age": 32, "recent_pace_min_per_km": 7.2, "usual_distance_km": 3.0}`
- Errors:
  - any value ≤ 0 → `{"error": "height_cm must be greater than 0."}`
- Example request: "키 170cm, 몸무게 68kg, 32살이고 요즘 1km에 7분 페이스로 3km 정도 뛰어."

## Tool: get_goal
- File: src/tools/goal_tools.py
- Purpose: Get the user's current running goal (target distance, time, and pace) and the target date if set.
- Type: read
- Parameters: none
- Returns: `{"distance_km": 10, "time_minutes": 50, "target_pace_min_per_km": 5.0, "target_date": "2026-12-01"}`
- Errors: no goal set → `{"error": "No goal set yet. Call set_goal first."}`
- Example request: "내 목표가 뭐였지?"

## Tool: set_goal
- File: src/tools/goal_tools.py
- Purpose: Set a running goal as a target distance within a target time. Only call after the user confirms.
- Type: write
- Parameters: distance_km (number, required); time_minutes (number, required); target_date (string, optional) — ISO date "YYYY-MM-DD" by which to achieve the goal
- Returns: `{"distance_km": 10, "time_minutes": 50, "target_pace_min_per_km": 5.0, "target_date": "2026-12-01"}`
- Errors:
  - distance_km ≤ 0 → `{"error": "distance_km must be greater than 0."}`
  - time_minutes ≤ 0 → `{"error": "time_minutes must be greater than 0."}`
- Example request: "10km를 50분 안에 뛰는 게 목표야. 12월 1일까지."

## Tool: get_courses
- File: src/tools/course_tools.py
- Purpose: Get local running courses, optionally filtered by difficulty or region. Stands in for a real map API.
- Type: read
- Parameters: difficulty (string, optional) — "평지", "완만한 언덕", or "언덕 많음"; region (string, optional) — matches if the course's region contains this text, e.g. "청주"
- Returns: `{"items": [{"name": "무심천 러닝코스", "distance_km": 5.0, "difficulty": "평지", "region": "청주", "description": "..."}]}`
- Errors: unknown difficulty → `{"error": "Unknown difficulty '산악'. Valid: 평지, 완만한 언덕, 언덕 많음."}`
- Errors: no region match → return an empty `items` list (not an error)
- Example request: "청주에서 평지 코스 추천해줘."

## Tool: plan_route
- File: src/tools/route_tools.py
- Purpose: Plan a real loop running route of about a given distance that starts and ends at a named place, using map data. Returns the measured distance, total climb, difficulty, and main roads.
- Type: read (external map APIs) + writes the route line to `data/route.json`
- Parameters: start (string, required) — start place name in Korea, e.g. "청주 무심천 체육공원"; distance_km (number, required) — desired route length, 1 to 30
- Returns: `{"start": "무심천 체육공원, 무심천 자전거길, 모충동", "requested_km": 5, "distance_km": 5.02, "ascent_m": 33, "difficulty": "평지", "main_roads": ["사운로", "무심천 자전거길", "충렬로"], "saved_to": "data/route.json"}`
- Errors:
  - distance_km outside 1–30 → `{"error": "distance_km must be between 1 and 30."}`
  - place not found → `{"error": "Place '없는장소' not found. Try a more specific name, e.g. '청주 무심천 체육공원'."}`
  - no walkable route → `{"error": "No walkable route found near '...'. Try a different start place."}`
  - network/service failure → `{"error": "Map service unavailable (...). Try again later, or use get_courses instead."}`
- How it works: Nominatim (place → coordinates) → OSRM foot router (loop through 3 points on a circle, tried in 4 directions and resized until the length matches; loops that double back on themselves are penalised) → Open-Meteo elevation (total climb).
- Difficulty: climb per km < 15 m → "평지", < 30 m → "완만한 언덕", otherwise "언덕 많음" (a rule of thumb, not an official grade).
- Example request: "무심천 체육공원에서 출발하는 5km 코스 짜줘."

## Tool: log_run
- File: src/tools/run_tools.py
- Purpose: Record a completed (or skipped) run with its distance and time. Only call after the user confirms.
- Type: write
- Parameters: distance_km (number, required); time_minutes (number, required); completed (boolean, optional, default true); date_str (string, optional) — "YYYY-MM-DD", defaults to today
- Returns: `{"date": "2026-10-01", "distance_km": 5.0, "time_minutes": 32.0, "pace_min_per_km": 6.4, "completed": true}`
- Errors:
  - distance_km ≤ 0 → `{"error": "distance_km must be greater than 0."}`
  - time_minutes ≤ 0 → `{"error": "time_minutes must be greater than 0."}`
- Example request: "오늘 5km를 32분에 뛰었어. 기록해 줘."

## Tool: get_progress_report
- File: src/tools/run_tools.py
- Purpose: Get a summary of all logged runs: how many runs, total distance, average pace, and the most recent run date.
- Type: read
- Parameters: none
- Returns: `{"total_runs": 4, "total_distance_km": 18.0, "avg_pace_min_per_km": 6.6, "last_run_date": "2026-10-01"}`
- Errors: no runs yet → return zeros and `"last_run_date": null` (not an error)
- Example request: "지금까지 얼마나 뛰었어?"

## Tool: generate_training_plan
- File: src/tools/plan_tools.py
- Purpose: Generate a weekly training schedule toward the current goal, based on the user's profile and how many days per week they want to train.
- Type: read
- Parameters: days_per_week (integer, required) — 1 to 7
- Returns: `{"days_per_week": 3, "target_pace_min_per_km": 5.0, "plan": [{"day": "월", "workout": "가벼운 조깅 3.0km"}, {"day": "수", "workout": "페이스 훈련 1.5km (목표 페이스 5.0분/km 근처로)"}, {"day": "금", "workout": "장거리 러닝 8.0km (여유 있는 페이스)"}]}`
- Errors:
  - no goal set → `{"error": "No goal set yet. Call set_goal first."}`
  - days_per_week out of 1–7 → `{"error": "days_per_week must be between 1 and 7."}`
- Example request: "주 3번 뛸 수 있어. 이번 주 훈련 계획 짜줘."

> Note: return a SUMMARY, not every record. Big tool results waste context.
