from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import IncidentState


class IncidentStore:
    def __init__(self, path: str | Path = ".incidentlens/incidents.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _setup(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save(self, state: IncidentState) -> None:
        payload = json.dumps(state.to_dict(), sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incidents(incident_id, scenario_id, status, state_json, updated_at)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(incident_id) DO UPDATE SET
                    scenario_id=excluded.scenario_id,
                    status=excluded.status,
                    state_json=excluded.state_json,
                    updated_at=excluded.updated_at
                """,
                (state.incident_id, state.scenario_id, state.status, payload, state.updated_at),
            )

    def load(self, incident_id: str) -> IncidentState:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state_json FROM incidents WHERE incident_id = ?", (incident_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Incident '{incident_id}' was not found")
        return IncidentState.from_dict(json.loads(row[0]))

