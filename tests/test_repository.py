"""Repository-level smoke tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "tapo_event_bridge"

def test_required_integration_files_exist() -> None:
    required = {
        "__init__.py", "config_flow.py", "const.py",
        "diagnostics.py", "manifest.json", "strings.json",
    }
    assert required.issubset({path.name for path in INTEGRATION.iterdir()})

def test_manifest_identity() -> None:
    manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["domain"] == "tapo_event_bridge"
    assert manifest["config_flow"] is True
    assert manifest["version"] == "0.1.0"

def test_translations_are_valid_json() -> None:
    for language in ("en", "fr"):
        path = INTEGRATION / "translations" / f"{language}.json"
        json.loads(path.read_text(encoding="utf-8"))
