"""Tool registry: the single place where tools are connected to the agent.

TOOL_SCHEMAS   -> sent to the LLM (what the model can SEE)
TOOL_FUNCTIONS -> used by agent.py (what actually RUNS)

When you add a tool: import its function and schema, then add both below.
"""
from src.tools.calculator import CALCULATE_SCHEMA, calculate
from src.tools.course_tools import GET_COURSES_SCHEMA, get_courses
from src.tools.goal_tools import GET_GOAL_SCHEMA, SET_GOAL_SCHEMA, get_goal, set_goal
from src.tools.plan_tools import GENERATE_TRAINING_PLAN_SCHEMA, generate_training_plan
from src.tools.profile_tools import GET_PROFILE_SCHEMA, SET_PROFILE_SCHEMA, get_profile, set_profile
from src.tools.route_tools import PLAN_ROUTE_SCHEMA, plan_route
from src.tools.run_tools import (
    GET_PROGRESS_REPORT_SCHEMA,
    LOG_RUN_SCHEMA,
    get_progress_report,
    log_run,
)

TOOL_SCHEMAS = [
    CALCULATE_SCHEMA,
    GET_PROFILE_SCHEMA,
    SET_PROFILE_SCHEMA,
    GET_GOAL_SCHEMA,
    SET_GOAL_SCHEMA,
    GET_COURSES_SCHEMA,
    PLAN_ROUTE_SCHEMA,
    LOG_RUN_SCHEMA,
    GET_PROGRESS_REPORT_SCHEMA,
    GENERATE_TRAINING_PLAN_SCHEMA,
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_profile": get_profile,
    "set_profile": set_profile,
    "get_goal": get_goal,
    "set_goal": set_goal,
    "get_courses": get_courses,
    "plan_route": plan_route,
    "log_run": log_run,
    "get_progress_report": get_progress_report,
    "generate_training_plan": generate_training_plan,
}
