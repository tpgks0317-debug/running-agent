"""Local running course tools (stands in for a real map API)."""
from src.tools.data_store import load

VALID_DIFFICULTIES = {"평지", "완만한 언덕", "언덕 많음"}


def get_courses(difficulty: str | None = None, region: str | None = None) -> dict:
    """Get local running courses, optionally filtered by difficulty or region."""
    if difficulty is not None and difficulty not in VALID_DIFFICULTIES:
        return {"error": f"Unknown difficulty '{difficulty}'. Valid: {', '.join(sorted(VALID_DIFFICULTIES))}."}

    courses = load("courses")
    items = [
        {"name": name, "distance_km": info["distance_km"], "difficulty": info["difficulty"],
         "region": info["region"], "description": info["description"]}
        for name, info in courses.items()
        if (difficulty is None or info["difficulty"] == difficulty)
        and (region is None or region in info["region"])
    ]
    return {"items": items}


GET_COURSES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_courses",
        "description": "Get local running courses, optionally filtered by difficulty or region. Stands in for a real map API.",
        "parameters": {
            "type": "object",
            "properties": {
                "difficulty": {"type": "string", "description": "'평지', '완만한 언덕', or '언덕 많음'"},
                "region": {"type": "string", "description": "Matches if the course's region contains this text, e.g. '청주'"},
            },
            "required": [],
        },
    },
}
