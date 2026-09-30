import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import jsonschema


DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "ruleset.schema.json"
DEFAULT_RULESETS_DIR = Path(__file__).resolve().parents[3] / "rulesets"


class RulesetValidationError(Exception):
    pass


class RulesetRegistry:
    def __init__(self, rulesets_dir: Optional[Path] = None, schema_path: Optional[Path] = None):
        self.rulesets_dir = Path(rulesets_dir) if rulesets_dir else DEFAULT_RULESETS_DIR
        self.schema_path = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
        self._schema: Optional[Dict[str, Any]] = None
        self._rulesets: Dict[str, Dict[str, Any]] = {}
        self.reload()

    def _load_schema(self) -> Dict[str, Any]:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Ruleset JSON Schema not found at {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def reload(self) -> None:
        """Reloads all rulesets from the rulesets directory dynamically."""
        self._schema = self._load_schema()
        self._rulesets.clear()

        if not self.rulesets_dir.exists():
            return

        for file_path in self.rulesets_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.validate_ruleset_data(data)
                ruleset_id = data["ruleset_id"]
                self._rulesets[ruleset_id] = data
            except Exception as e:
                # Log or re-raise
                print(f"Warning: Failed to load ruleset from {file_path}: {e}")

    def validate_ruleset_data(self, data: Dict[str, Any]) -> None:
        if self._schema is None:
            self._schema = self._load_schema()
        try:
            jsonschema.validate(instance=data, schema=self._schema)
        except jsonschema.ValidationError as e:
            raise RulesetValidationError(f"Ruleset failed schema validation: {e.message}") from e

    def register_ruleset(self, data: Dict[str, Any], save_to_disk: bool = True) -> str:
        self.validate_ruleset_data(data)
        ruleset_id = data["ruleset_id"]
        if save_to_disk:
            self.rulesets_dir.mkdir(parents=True, exist_ok=True)
            target_path = self.rulesets_dir / f"{ruleset_id}.json"
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        self._rulesets[ruleset_id] = data
        return ruleset_id

    def get_ruleset(self, ruleset_id: str) -> Dict[str, Any]:
        if ruleset_id not in self._rulesets:
            # Try reloading in case a file was dropped into the directory live!
            self.reload()
        if ruleset_id not in self._rulesets:
            raise KeyError(f"Ruleset '{ruleset_id}' not found in registry. Available: {list(self._rulesets.keys())}")
        return self._rulesets[ruleset_id]

    def list_rulesets(self) -> List[Dict[str, str]]:
        # Refresh to detect newly dropped files
        self.reload()
        return [
            {
                "ruleset_id": r_id,
                "edition": r["edition"],
                "title": r["title"],
                "citation": r.get("citation", "")
            }
            for r_id, r in self._rulesets.items()
        ]


# Singleton instance
ruleset_registry = RulesetRegistry()
