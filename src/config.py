"""Load project settings from the .env file."""
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.md"

# On Vercel only /tmp is writable, so work on a copy of data/ there.
# The copy starts fresh whenever Vercel starts a new server instance.
if os.getenv("VERCEL"):
    DATA_DIR = Path("/tmp/data")
    if not DATA_DIR.exists():
        shutil.copytree(PROJECT_ROOT / "data", DATA_DIR)

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

# Map services used by plan_route (all free, no API key needed)
GEOCODE_URL = os.getenv("GEOCODE_URL", "https://nominatim.openstreetmap.org/search")
ROUTE_URL = os.getenv("ROUTE_URL", "https://routing.openstreetmap.de/routed-foot/route/v1/foot")
ELEVATION_URL = os.getenv("ELEVATION_URL", "https://api.open-meteo.com/v1/elevation")
MAP_USER_AGENT = os.getenv("MAP_USER_AGENT", "running-agent/0.1 (student project)")
MAP_TIMEOUT_SECONDS = int(os.getenv("MAP_TIMEOUT_SECONDS", "15"))

if not API_KEY:
    raise RuntimeError(
        "API_KEY is missing. Copy .env.example to .env and put your API key in it."
    )
