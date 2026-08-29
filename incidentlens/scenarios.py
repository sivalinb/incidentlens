from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


class ScenarioCatalog:
    def __init__(self) -> None:
        self.root = files("incidentlens").joinpath("scenarios")

    def list(self) -> list[dict[str, str]]:
        items = []
        for path in sorted(self.root.iterdir(), key=lambda item: item.name):
            if path.name.endswith(".json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                items.append({"id": data["id"], "title": data["title"]})
        return items

    def load(self, scenario_id: str) -> dict[str, Any]:
        path = self.root.joinpath(f"{scenario_id}.json")
        if not path.is_file():
            choices = ", ".join(item["id"] for item in self.list())
            raise ValueError(f"Unknown scenario '{scenario_id}'. Choose one of: {choices}")
        return json.loads(path.read_text(encoding="utf-8"))

