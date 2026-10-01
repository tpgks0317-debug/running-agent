"""Running goal tools."""
from src.tools.data_store import load, save


def get_goal() -> dict:
    """Get the user's current running goal and target pace."""
    goal = load("goal")
    if not goal:
        return {"error": "No goal set yet. Call set_goal first."}
    return {**goal, "target_pace_min_per_km": round(goal["time_minutes"] / goal["distance_km"], 2)}


GET_GOAL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_goal",
        "description": "Get the user's current running goal (target distance, time, and pace) and the target date if set.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def set_goal(distance_km: float, time_minutes: float, target_date: str | None = None) -> dict:
    """Set a running goal as a target distance within a target time."""
    if distance_km <= 0:
        return {"error": "distance_km must be greater than 0."}
    if time_minutes <= 0:
        return {"error": "time_minutes must be greater than 0."}

    goal = {"distance_km": distance_km, "time_minutes": time_minutes}
    if target_date is not None:
        goal["target_date"] = target_date
    save("goal", goal)
    return {**goal, "target_pace_min_per_km": round(time_minutes / distance_km, 2)}


SET_GOAL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "set_goal",
        "description": "Set a running goal as a target distance within a target time. Only call after the user confirms.",
        "parameters": {
            "type": "object",
            "properties": {
                "distance_km": {"type": "number", "description": "Target distance in km"},
                "time_minutes": {"type": "number", "description": "Target time in minutes"},
                "target_date": {"type": "string", "description": "ISO date 'YYYY-MM-DD' by which to achieve the goal"},
            },
            "required": ["distance_km", "time_minutes"],
        },
    },
}
