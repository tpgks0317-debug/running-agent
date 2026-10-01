"""The agent: keeps conversation history and runs the tool-calling loop."""
import json

from src import config
from src.llm_client import chat
from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS


class CafeAgent:
    def __init__(self, on_tool_call=None):
        self.system_prompt = config.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.history: list = []  # user, assistant, and tool messages (NOT the system prompt)
        self.on_tool_call = on_tool_call  # optional callback(name, arguments_json, result) for UIs

    def _trim_history(self) -> list:
        """Keep only the last MAX_HISTORY_MESSAGES messages, without splitting an
        assistant tool_call message from the tool results that answer it."""
        n = config.MAX_HISTORY_MESSAGES
        if len(self.history) <= n:
            return list(self.history)
        start = len(self.history) - n
        while start > 0 and self.history[start]["role"] == "tool":
            start -= 1
        return self.history[start:]

    def _build_context(self) -> list:
        """Return the messages to send to the LLM: system prompt + (trimmed) history."""
        return [{"role": "system", "content": self.system_prompt}] + self._trim_history()

    def _execute_tool(self, name: str, arguments_json: str) -> dict:
        """Run one tool safely. Never raise: return {"error": ...} on any problem."""
        func = TOOL_FUNCTIONS.get(name)
        if func is None:
            return {"error": f"Unknown tool '{name}'."}
        try:
            arguments = json.loads(arguments_json) if arguments_json else {}
            return func(**arguments)
        except Exception as e:
            return {"error": f"Tool '{name}' failed: {e}"}

    def run(self, user_input: str) -> str:
        """Handle one user message and return the final answer text."""
        self.history.append({"role": "user", "content": user_input})

        for _ in range(config.MAX_TOOL_ROUNDS):
            response = chat(self._build_context(), TOOL_SCHEMAS)

            assistant_msg = {"role": "assistant", "content": response.content}
            if response.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in response.tool_calls
                ]
            self.history.append(assistant_msg)

            if not response.tool_calls:
                return response.content

            for tc in response.tool_calls:
                result = self._execute_tool(tc.function.name, tc.function.arguments)
                print(f"🔧 {tc.function.name}({tc.function.arguments}) → {json.dumps(result, ensure_ascii=False)}")
                if self.on_tool_call:
                    self.on_tool_call(tc.function.name, tc.function.arguments, result)
                self.history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        return "Sorry, I could not finish this request."
