import json
from pathlib import Path

DATA_PATH = Path(__file__).parent

def load_json(filename: str):
    with open(DATA_PATH / filename, "r", encoding="utf-8") as f:
        return json.load(f)

# примеры загрузки
all_data = load_json("all.json")
lines_data = load_json("lines.json")
areas_data = load_json("areas.json")
points_data = load_json("points.json")
relief_data = load_json("relief.json")
water_data = load_json("water.json")

