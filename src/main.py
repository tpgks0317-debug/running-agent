"""Command-line chat with the café agent."""
from src.agent import CafeAgent


def main():
    agent = CafeAgent()
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("exit", "quit"):
            break
        print("Agent: " + agent.run(user_input))


if __name__ == "__main__":
    main()
