"""Basic schema validation smoke tests."""

from schemas import ProjectInput, RequirementsResult


def test_project_input():
    project = ProjectInput.model_validate({
        "projectName": "IntelliSE",
        "projectDescription": (
            "An AI-powered system for software requirements "
            "analysis and documentation."
        ),
    })
    assert project.project_name == "IntelliSE"


def test_requirements_result():
    result = RequirementsResult.model_validate({
        "functionalRequirements": [
            {
                "type": "functional",
                "description": "The system shall generate requirements.",
                "priority": "must",
                "rationale": "This is a core system feature.",
                "source": "explicit",
            }
        ],
        "nonFunctionalRequirements": [
            {
                "type": "non_functional",
                "description": "The system shall respond within 5 seconds.",
                "priority": "should",
                "rationale": "This improves system performance.",
                "source": "explicit",
            }
        ],
    })
    assert len(result.functional_requirements) == 1
    assert len(result.non_functional_requirements) == 1
