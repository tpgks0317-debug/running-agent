"""Web chat UI for the café agent (Flask). Run with `py -m src.web`."""
import os
import uuid

from flask import Flask, jsonify, render_template, request, session

from src.agent import CafeAgent
from src.tools.data_store import load

app = Flask(__name__)
app.secret_key = os.urandom(24)

_agents: dict[str, CafeAgent] = {}  # session_id -> CafeAgent (server-side, in-memory)


def _get_agent() -> CafeAgent:
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    session_id = session["session_id"]
    if session_id not in _agents:
        _agents[session_id] = CafeAgent()
    return _agents[session_id]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    message = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    tool_calls = []

    def on_tool_call(name, arguments_json, result):
        tool_calls.append({"name": name, "arguments": arguments_json, "result": result})

    agent = _get_agent()
    agent.on_tool_call = on_tool_call
    reply = agent.run(message)

    # If a route was planned in this turn, send its line along so the page can draw it on a map.
    planned = any(tc["name"] == "plan_route" and "error" not in tc["result"] for tc in tool_calls)
    route = load("route") if planned else None

    return jsonify({"reply": reply, "tool_calls": tool_calls, "route": route})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    session_id = session.get("session_id")
    if session_id in _agents:
        del _agents[session_id]
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Local default: http://127.0.0.1:5000. A hosting service sets HOST/PORT itself.
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")),
            debug=os.getenv("FLASK_DEBUG") == "1")
