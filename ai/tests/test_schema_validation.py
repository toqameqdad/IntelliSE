"""Focused validation tests for AI service input and output contracts."""

import pytest
from pydantic import ValidationError

from schemas import (
    DiagramGenerationInput,
    RequirementsResult,
    ContextDiagramResult,
    ActivityDiagramResult,
)


def test_diagram_input_preserves_existing_json_shape():
    payload = {"projectName": "Demo", "functionalRequirements": [{"id": "FR-001"}]}
    assert DiagramGenerationInput.model_validate(payload).root == payload


@pytest.mark.parametrize("payload", [{}, [], "text", None])
def test_diagram_input_rejects_invalid_root(payload):
    with pytest.raises(ValidationError):
        DiagramGenerationInput.model_validate(payload)


def test_requirements_reject_wrong_type_in_functional_list():
    with pytest.raises(ValidationError):
        RequirementsResult.model_validate({
            "functionalRequirements": [{
                "type": "non_functional",
                "description": "A requirement",
                "priority": "must",
                "rationale": "Needed",
                "source": "explicit",
            }],
            "nonFunctionalRequirements": [],
        })


def test_requirements_reject_duplicate_descriptions():
    item = {
        "type": "functional",
        "description": "Create project",
        "priority": "must",
        "rationale": "Needed",
        "source": "explicit",
    }
    with pytest.raises(ValidationError):
        RequirementsResult.model_validate({
            "functionalRequirements": [item, item],
            "nonFunctionalRequirements": [],
        })


def test_context_rejects_unknown_flow_endpoint():
    with pytest.raises(ValidationError):
        ContextDiagramResult.model_validate({
            "diagramType": "context",
            "system": {"id": "system", "name": "Demo", "description": "System"},
            "externalEntities": [],
            "dataFlows": [{
                "id": "f1", "source": "missing", "target": "system", "label": "data"
            }],
        })


def _activity_payload():
    return {
        "diagramType": "activity",
        "systemName": "Demo",
        "activityName": "Workflow",
        "nodes": [
            {"id": "start", "name": "Start", "description": "Start", "nodeType": "initial"},
            {"id": "task", "name": "Task", "description": "Task", "nodeType": "action"},
            {"id": "end", "name": "End", "description": "End", "nodeType": "activity_final"},
        ],
        "flows": [
            {"source": "start", "target": "task"},
            {"source": "task", "target": "end"},
        ],
    }


def test_activity_accepts_valid_linear_workflow():
    assert ActivityDiagramResult.model_validate(_activity_payload()).activity_name == "Workflow"


def test_activity_rejects_unreachable_node():
    payload = _activity_payload()
    payload["nodes"].append({
        "id": "orphan", "name": "Orphan", "description": "Unused", "nodeType": "action"
    })
    with pytest.raises(ValidationError, match="Unreachable"):
        ActivityDiagramResult.model_validate(payload)


def test_activity_rejects_decision_without_conditions():
    payload = _activity_payload()
    payload["nodes"][1]["nodeType"] = "decision"
    payload["flows"].append({"source": "task", "target": "start"})
    with pytest.raises(ValidationError, match="conditions"):
        ActivityDiagramResult.model_validate(payload)
