"""Training plan generator — the tool a café or medication agent would never need."""
from src.tools.data_store import load

DAY_PATTERNS = {
    1: ["월"],
    2: ["월", "목"],
    3: ["월", "수", "금"],
    4: ["월", "화", "목", "금"],
    5: ["월", "화", "수", "금", "토"],
    6: ["월", "화", "수", "목", "금", "토"],
    7: ["월", "화", "수", "목", "금", "토", "일"],
}


def generate_training_plan(days_per_week: int) -> dict:
    """Generate a weekly training schedule toward the current goal."""
    if days_per_week not in DAY_PATTERNS:
        return {"error": "days_per_week must be between 1 and 7."}

    goal = load("goal")
    if not goal:
        return {"error": "No goal set yet. Call set_goal first."}

    profile = load("profile")
    target_pace = round(goal["time_minutes"] / goal["distance_km"], 2)
    easy_distance = profile["usual_distance_km"]
    long_distance = round(max(goal["distance_km"] * 0.8, easy_distance), 1)
    interval_distance = round(max(easy_distance / 2, 1), 1)

    days = DAY_PATTERNS[days_per_week]
    plan = []
    for i, day in enumerate(days):
        if i == len(days) - 1:
            workout = f"장거리 러닝 {long_distance}km (여유 있는 페이스)"
        elif i == 0:
            workout = f"가벼운 조깅 {easy_distance}km"
        else:
            workout = f"페이스 훈련 {interval_distance}km (목표 페이스 {target_pace}분/km 근처로)"
        plan.append({"day": day, "workout": workout})

    return {"days_per_week": days_per_week, "target_pace_min_per_km": target_pace, "plan": plan}


GENERATE_TRAINING_PLAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_training_plan",
        "description": "Generate a weekly training schedule toward the current goal, based on the user's profile and how many days per week they want to train.",
        "parameters": {
            "type": "object",
            "properties": {
                "days_per_week": {"type": "integer", "description": "How many days per week to train, 1 to 7"},
            },
            "required": ["days_per_week"],
        },
    },
}
