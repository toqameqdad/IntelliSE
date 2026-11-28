"""API contract tests without calling Gemini."""

import importlib.util
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api(monkeypatch):
    fake_gemini = types.ModuleType("gemini_service")
    functions = (
        "analyze_project",
        "generate_requirements",
        "reanalyze_project",
        "generate_srs",
        "generate_context_diagram",
        "generate_use_case_diagram",
        "generate_activity_diagram",
        "generate_object_diagram",
        "recommend_methodology",
        "analyze_methodology_compatibility",
    )

    def unavailable(*args, **kwargs):
        raise RuntimeError("private Gemini error details")

    for name in functions:
        setattr(fake_gemini, name, unavailable)

    monkeypatch.setitem(sys.modules, "gemini_service", fake_gemini)
    spec = importlib.util.spec_from_file_location(
        "_intellise_api_under_test", Path(__file__).resolve().parents[1] / "main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, TestClient(module.app)


@pytest.mark.parametrize(
    "path",
    [
        "/api/ai/diagrams/context/generate",
        "/api/ai/diagrams/use-case/generate",
        "/api/ai/diagrams/activity/generate",
        "/api/ai/diagrams/object/generate",
        "/generate-activity-diagram",
        "/generate-object-diagram",
    ],
)
def test_diagram_errors_do_not_leak_exception_details(api, path):
    _, client = api
    response = client.post(path, json={"projectName": "Example"})
    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "AI_GENERATION_FAILED"
    assert "private Gemini error details" not in str(body)


@pytest.mark.parametrize(
    "path",
    [
        "/api/ai/diagrams/context/generate",
        "/api/ai/diagrams/use-case/generate",
        "/api/ai/diagrams/activity/generate",
        "/api/ai/diagrams/object/generate",
    ],
)
def test_diagram_routes_reject_empty_objects(api, path):
    _, client = api
    response = client.post(path, json={})
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_INPUT"


def test_legacy_routes_are_hidden_from_openapi(api):
    _, client = api
    paths = client.get("/openapi.json").json()["paths"]
    assert "/generate-activity-diagram" not in paths
    assert "/generate-object-diagram" not in paths
    assert "/api/ai/diagrams/activity/generate" in paths
    assert "/api/ai/diagrams/object/generate" in paths


def test_diagram_request_preserves_payload(api, monkeypatch):
    module, client = api
    captured = {}

    def fake_generate(payload):
        import json

        captured["data"] = json.loads(payload)
        return {
            "diagramType": "context",
            "system": {"id": "system", "name": "Example", "description": "System"},
            "externalEntities": [],
            "dataFlows": [],
        }

    monkeypatch.setattr(module, "generate_context_diagram", fake_generate)
    payload = {"projectName": "Example", "nested": {"value": 1}}
    response = client.post("/api/ai/diagrams/context/generate", json=payload)
    assert response.status_code == 200, response.text
    assert captured["data"] == payload
