"""User profile tools."""
from src.tools.data_store import load, save


def get_profile() -> dict:
    """Get the user's body stats and current running ability."""
    return load("profile")


GET_PROFILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_profile",
        "description": "Get the user's body stats and current running ability (height, weight, age, recent pace, usual distance).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def set_profile(
    height_cm: float,
    weight_kg: float,
    age: int,
    recent_pace_min_per_km: float,
    usual_distance_km: float,
) -> dict:
    """Update the user's body stats and current running ability."""
    if height_cm <= 0:
        return {"error": "height_cm must be greater than 0."}
    if weight_kg <= 0:
        return {"error": "weight_kg must be greater than 0."}
    if age <= 0:
        return {"error": "age must be greater than 0."}
    if recent_pace_min_per_km <= 0:
        return {"error": "recent_pace_min_per_km must be greater than 0."}
    if usual_distance_km <= 0:
        return {"error": "usual_distance_km must be greater than 0."}

    profile = {
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "age": age,
        "recent_pace_min_per_km": recent_pace_min_per_km,
        "usual_distance_km": usual_distance_km,
    }
    save("profile", profile)
    return profile


SET_PROFILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "set_profile",
        "description": "Update the user's body stats and current running ability. Only call after the user confirms.",
        "parameters": {
            "type": "object",
            "properties": {
                "height_cm": {"type": "number", "description": "Height in centimeters"},
                "weight_kg": {"type": "number", "description": "Weight in kilograms"},
                "age": {"type": "integer", "description": "Age in years"},
                "recent_pace_min_per_km": {"type": "number", "description": "Recent running pace, minutes per km"},
                "usual_distance_km": {"type": "number", "description": "Distance usually run in one session, km"},
            },
            "required": ["height_cm", "weight_kg", "age", "recent_pace_min_per_km", "usual_distance_km"],
        },
    },
}
