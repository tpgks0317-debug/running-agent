"""Run log tools."""
from datetime import date

from src.tools.data_store import load, save


def log_run(distance_km: float, time_minutes: float, completed: bool = True, date_str: str | None = None) -> dict:
    """Record a completed (or skipped) run with its distance and time."""
    if distance_km <= 0:
        return {"error": "distance_km must be greater than 0."}
    if time_minutes <= 0:
        return {"error": "time_minutes must be greater than 0."}

    run_date = date_str or str(date.today())
    record = {"date": run_date, "distance_km": distance_km, "time_minutes": time_minutes, "completed": completed}

    runs = load("runs")
    runs.setdefault("records", []).append(record)
    save("runs", runs)

    return {**record, "pace_min_per_km": round(time_minutes / distance_km, 2)}


LOG_RUN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "log_run",
        "description": "Record a completed (or skipped) run with its distance and time. Only call after the user confirms.",
        "parameters": {
            "type": "object",
            "properties": {
                "distance_km": {"type": "number", "description": "Distance run, in km"},
                "time_minutes": {"type": "number", "description": "Time taken, in minutes"},
                "completed": {"type": "boolean", "description": "False means the run was skipped/not finished. Defaults to true."},
                "date_str": {"type": "string", "description": "ISO date 'YYYY-MM-DD'. Defaults to today."},
            },
            "required": ["distance_km", "time_minutes"],
        },
    },
}


def get_progress_report() -> dict:
    """Return a SHORT summary of all logged runs (not every record)."""
    runs = load("runs")
    records = runs.get("records", [])

    if not records:
        return {"total_runs": 0, "total_distance_km": 0, "avg_pace_min_per_km": 0, "last_run_date": None}

    total_distance = sum(r["distance_km"] for r in records)
    total_time = sum(r["time_minutes"] for r in records)

    return {
        "total_runs": len(records),
        "total_distance_km": round(total_distance, 2),
        "avg_pace_min_per_km": round(total_time / total_distance, 2),
        "last_run_date": records[-1]["date"],
    }


GET_PROGRESS_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_progress_report",
        "description": "Get a summary of all logged runs: how many runs, total distance, average pace, and the most recent run date.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}
