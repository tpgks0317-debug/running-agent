"""Tool tests. No LLM needed.
Run one group:  python -m pytest tests -k get_profile
"""
from src.tools.calculator import calculate


# ---- Already done ----
def test_calculate_ok():
    assert calculate("3 * 4500 * 0.9")["result"] == 12150.0


def test_calculate_error_has_hint():
    assert "error" in calculate("import os")


# ---- Data store ----
def test_data_store_roundtrip():
    from src.tools import data_store
    data = data_store.load("profile")
    data["age"] = 99
    data_store.save("profile", data)
    assert data_store.load("profile")["age"] == 99


# ---- get_profile / set_profile ----
def test_get_profile_ok():
    from src.tools.profile_tools import get_profile
    p = get_profile()
    assert p["height_cm"] == 170 and p["usual_distance_km"] == 3.0


def test_set_profile_ok():
    from src.tools.profile_tools import set_profile
    r = set_profile(175, 70, 30, 6.5, 4.0)
    assert r == {"height_cm": 175, "weight_kg": 70, "age": 30, "recent_pace_min_per_km": 6.5, "usual_distance_km": 4.0}


def test_set_profile_bad_value():
    from src.tools.profile_tools import set_profile
    assert "error" in set_profile(-1, 70, 30, 6.5, 4.0)


# ---- get_goal / set_goal ----
def test_get_goal_not_set():
    from src.tools.goal_tools import get_goal
    assert "error" in get_goal()


def test_set_goal_ok():
    from src.tools.goal_tools import set_goal
    r = set_goal(10, 50, target_date="2026-12-01")
    assert r["target_pace_min_per_km"] == 5.0 and r["target_date"] == "2026-12-01"


def test_get_goal_after_set():
    from src.tools.goal_tools import get_goal, set_goal
    set_goal(10, 50)
    assert get_goal()["target_pace_min_per_km"] == 5.0


def test_set_goal_bad_distance():
    from src.tools.goal_tools import set_goal
    assert "error" in set_goal(0, 50)


# ---- get_courses ----
def test_get_courses_all():
    from src.tools.course_tools import get_courses
    assert len(get_courses()["items"]) == 8


def test_get_courses_difficulty():
    from src.tools.course_tools import get_courses
    items = get_courses(difficulty="평지")["items"]
    assert {i["name"] for i in items} == {"무심천 러닝코스", "운천 신봉 하천길", "한강 반포 코스", "해운대 해변 코스"}


def test_get_courses_region():
    from src.tools.course_tools import get_courses
    items = get_courses(region="청주")["items"]
    assert len(items) == 4


def test_get_courses_bad_difficulty():
    from src.tools.course_tools import get_courses
    assert "error" in get_courses(difficulty="산악")


def test_get_courses_no_match_not_error():
    from src.tools.course_tools import get_courses
    assert get_courses(region="제주")["items"] == []


# ---- plan_route (map services are faked — tests never touch the network) ----
def _fake_map(monkeypatch, places=True, route_km=5.1):
    from src import config
    from src.tools import route_tools

    def fake_get_json(url, params):
        if url == config.GEOCODE_URL:
            return [{"lat": "36.639", "lon": "127.483", "display_name": "무심천 체육공원, 모충동, 청주시, 충청북도"}] if places else []
        if url == config.ELEVATION_URL:
            return {"elevation": [40.0, 50.0, 45.0, 60.0]}
        return {"code": "Ok", "routes": [{
            "distance": route_km * 1000,
            "geometry": {"coordinates": [[127.483, 36.639], [127.49, 36.64], [127.49, 36.65], [127.483, 36.639]]},
            "legs": [{"steps": [{"name": "무심천 자전거길", "distance": 3000}, {"name": "흥덕로", "distance": 2000},
                                {"name": "", "distance": 100}]}],
        }]}

    monkeypatch.setattr(route_tools, "_get_json", fake_get_json)


def test_plan_route_ok(monkeypatch, temp_data):
    from src.tools.route_tools import plan_route
    _fake_map(monkeypatch)
    r = plan_route("청주 무심천 체육공원", 5)
    assert r["start"] == "무심천 체육공원, 모충동, 청주시"
    assert r["distance_km"] == 5.1 and r["requested_km"] == 5
    assert r["ascent_m"] == 25 and r["difficulty"] == "평지"
    assert r["main_roads"] == ["무심천 자전거길", "흥덕로"]
    assert (temp_data / "route.json").exists()


def test_plan_route_place_not_found(monkeypatch):
    from src.tools.route_tools import plan_route
    _fake_map(monkeypatch, places=False)
    assert "not found" in plan_route("없는장소", 5)["error"]


def test_plan_route_bad_distance():
    from src.tools.route_tools import plan_route
    assert "error" in plan_route("청주 무심천 체육공원", 0)
    assert "error" in plan_route("청주 무심천 체육공원", 100)


def test_plan_route_service_down(monkeypatch):
    from src.tools import route_tools

    def boom(url, params):
        raise OSError("timed out")

    monkeypatch.setattr(route_tools, "_get_json", boom)
    assert "unavailable" in route_tools.plan_route("청주 무심천 체육공원", 5)["error"]


# ---- log_run / get_progress_report ----
def test_log_run_ok():
    from src.tools.run_tools import log_run
    r = log_run(5.0, 32.0, date_str="2026-10-01")
    assert r == {"date": "2026-10-01", "distance_km": 5.0, "time_minutes": 32.0, "completed": True, "pace_min_per_km": 6.4}


def test_log_run_bad_distance():
    from src.tools.run_tools import log_run
    assert "error" in log_run(0, 32.0)


def test_progress_report_empty():
    from src.tools.run_tools import get_progress_report
    r = get_progress_report()
    assert r == {"total_runs": 0, "total_distance_km": 0, "avg_pace_min_per_km": 0, "last_run_date": None}


def test_progress_report_summary():
    from src.tools.run_tools import log_run, get_progress_report
    log_run(5.0, 32.0, date_str="2026-10-01")
    log_run(3.0, 21.0, date_str="2026-10-02")
    r = get_progress_report()
    assert r["total_runs"] == 2 and r["total_distance_km"] == 8.0 and r["last_run_date"] == "2026-10-02"


# ---- generate_training_plan (my tool) ----
def test_generate_training_plan_no_goal():
    from src.tools.plan_tools import generate_training_plan
    assert "error" in generate_training_plan(3)


def test_generate_training_plan_ok():
    from src.tools.goal_tools import set_goal
    from src.tools.plan_tools import generate_training_plan
    set_goal(10, 50)
    r = generate_training_plan(3)
    assert r["days_per_week"] == 3 and r["target_pace_min_per_km"] == 5.0
    assert [p["day"] for p in r["plan"]] == ["월", "수", "금"]
    assert "장거리" in r["plan"][-1]["workout"]


def test_generate_training_plan_bad_days():
    from src.tools.goal_tools import set_goal
    from src.tools.plan_tools import generate_training_plan
    set_goal(10, 50)
    assert "error" in generate_training_plan(8)


# ---- Registry check ----
def test_registry_consistent():
    from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS
    names = {s["function"]["name"] for s in TOOL_SCHEMAS}
    assert names == set(TOOL_FUNCTIONS)
    assert len(names) >= 8
