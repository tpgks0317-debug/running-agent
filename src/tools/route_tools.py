"""Route planning tool backed by OpenStreetMap services (geocoding, foot routing, elevation)."""
import json
import math
import urllib.parse
import urllib.request

from src import config
from src.tools.data_store import save

MIN_KM, MAX_KM = 1, 30
BEARINGS = (0, 90, 180, 270)  # directions to try for the loop
DETOUR = 1.3                  # real roads are ~30% longer than the straight line
GOOD_ENOUGH = 0.05            # stop refining once within 5% of the requested distance
ELEVATION_SAMPLES = 100       # the elevation API accepts up to 100 points per call
NOISE_M = 3.0                 # ignore climbs smaller than this (elevation data noise)


def _get_json(url: str, params: dict):
    """GET a JSON document from a map service."""
    request = urllib.request.Request(
        url + "?" + urllib.parse.urlencode(params), headers={"User-Agent": config.MAP_USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=config.MAP_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _geocode(place: str):
    """Turn a place name into (lat, lon, short display name), or None if not found."""
    hits = _get_json(config.GEOCODE_URL, {"q": place, "format": "jsonv2", "limit": 1,
                                          "accept-language": "ko", "countrycodes": "kr"})
    if not hits:
        return None
    name = ", ".join(hits[0]["display_name"].split(", ")[:3])
    return float(hits[0]["lat"]), float(hits[0]["lon"]), name


def _offset(lat: float, lon: float, bearing_deg: float, km: float) -> tuple:
    """Move `km` from a point in the direction `bearing_deg` (0 = north)."""
    bearing = math.radians(bearing_deg)
    return (lat + km * math.cos(bearing) / 111.32,
            lon + km * math.sin(bearing) / (111.32 * math.cos(math.radians(lat))))


def _loop_points(lat: float, lon: float, bearing: float, radius_km: float) -> list:
    """Start, three points on a circle through the start, then back to the start."""
    centre = _offset(lat, lon, bearing, radius_km)
    ring = [_offset(*centre, bearing + 180 + angle, radius_km) for angle in (90, 180, 270)]
    return [(lat, lon)] + ring + [(lat, lon)]


def _route(points: list):
    """Ask the foot router for a path through `points`. Returns None if there is none."""
    path = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
    data = _get_json(f"{config.ROUTE_URL}/{path}", {"overview": "full", "geometries": "geojson", "steps": "true"})
    if data.get("code") != "Ok":
        return None
    roads: dict = {}
    for leg in data["routes"][0]["legs"]:
        for step in leg["steps"]:
            if step.get("name"):
                roads[step["name"]] = roads.get(step["name"], 0) + step["distance"]
    return {"km": data["routes"][0]["distance"] / 1000,
            "coords": data["routes"][0]["geometry"]["coordinates"],
            "roads": sorted(roads, key=roads.get, reverse=True)[:3]}


def _overlap(coords: list) -> float:
    """Share of the route that is run twice (dead-end spurs make a poor loop)."""
    seen, repeated, total = set(), 0, 0
    for a, b in zip(coords, coords[1:]):
        segment = tuple(sorted([(round(a[0], 5), round(a[1], 5)), (round(b[0], 5), round(b[1], 5))]))
        if segment[0] == segment[1]:
            continue
        total += 1
        repeated += segment in seen
        seen.add(segment)
    return repeated / total if total else 0.0


def _best_loop(lat: float, lon: float, target_km: float):
    """Try loops in each direction, resizing toward the target; return the best one."""
    best, best_score = None, None
    for bearing in BEARINGS:
        radius = target_km / (2 * math.pi) / DETOUR
        for _ in range(3):
            route = _route(_loop_points(lat, lon, bearing, radius))
            if route is None:
                break
            miss = abs(route["km"] - target_km) / target_km
            score = miss + _overlap(route["coords"])
            if best is None or score < best_score:
                best, best_score = route, score
            if miss < GOOD_ENOUGH:
                break
            radius *= target_km / route["km"]
        if best is not None and best_score < 2 * GOOD_ENOUGH:
            break
    return best


def _ascent_m(coords: list) -> float:
    """Total climb along the route in metres."""
    points = coords[::max(1, len(coords) // ELEVATION_SAMPLES)][:ELEVATION_SAMPLES]
    heights = _get_json(config.ELEVATION_URL, {"latitude": ",".join(f"{p[1]:.5f}" for p in points),
                                               "longitude": ",".join(f"{p[0]:.5f}" for p in points)})["elevation"]
    total, reference = 0.0, heights[0]
    for height in heights[1:]:
        if height - reference >= NOISE_M:
            total += height - reference
            reference = height
        elif reference - height >= NOISE_M:
            reference = height
    return total


def _difficulty(ascent_m_per_km: float) -> str:
    """Map climb per km onto the same labels get_courses uses."""
    if ascent_m_per_km < 15:
        return "평지"
    return "완만한 언덕" if ascent_m_per_km < 30 else "언덕 많음"


def plan_route(start: str, distance_km: float) -> dict:
    """Plan a real loop running route of about distance_km that starts and ends at a place."""
    if not MIN_KM <= distance_km <= MAX_KM:
        return {"error": f"distance_km must be between {MIN_KM} and {MAX_KM}."}
    try:
        place = _geocode(start)
        if place is None:
            return {"error": f"Place '{start}' not found. Try a more specific name, e.g. '청주 무심천 체육공원'."}
        lat, lon, name = place
        route = _best_loop(lat, lon, distance_km)
        if route is None:
            return {"error": f"No walkable route found near '{name}'. Try a different start place."}
        ascent = _ascent_m(route["coords"])
    except (OSError, ValueError, KeyError) as e:
        return {"error": f"Map service unavailable ({e}). Try again later, or use get_courses instead."}

    result = {"start": name, "requested_km": distance_km, "distance_km": round(route["km"], 2),
              "ascent_m": round(ascent), "difficulty": _difficulty(ascent / route["km"]),
              "main_roads": route["roads"]}
    save("route", {"type": "Feature", "properties": result,
                   "geometry": {"type": "LineString", "coordinates": route["coords"]}})
    return {**result, "saved_to": "data/route.json"}


PLAN_ROUTE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "plan_route",
        "description": "Plan a real loop running route of about a given distance that starts and ends at a named place, using map data. Returns the measured distance, total climb, difficulty, and main roads.",
        "parameters": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "Start place name in Korea, e.g. '청주 무심천 체육공원'"},
                "distance_km": {"type": "number", "description": "Desired route length in km, 1 to 30"},
            },
            "required": ["start", "distance_km"],
        },
    },
}
