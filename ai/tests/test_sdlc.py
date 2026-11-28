
import pytest

from schemas import SDLCPhase, SDLCPlanResult
from gemini_service import (
    redistribute_sdlc_duration,
    SDLC_PHASE_WEIGHTS,
    generate_sdlc_plan,
)

from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from schemas import SDLCPlanInput, SDLCPlanResult, SDLCDurationUpdateInput


client = TestClient(app)

@pytest.fixture
def sample_plan():
    phase_names = [
        "Requirements Analysis",
        "System Design",
        "Implementation",
        "Testing",
        "Deployment",
        "Maintenance",
    ]

    durations = [3, 3, 6, 4, 2, 2]

    phases = [
        SDLCPhase(
            name=name,
            objectives=["Complete phase objectives"],
            activities=["Perform phase activities"],
            deliverables=["Produce phase deliverables"],
            estimated_duration_weeks=duration,
        )
        for name, duration in zip(phase_names, durations)
    ]

    return SDLCPlanResult(
        methodology="Waterfall",
        total_duration_weeks=20,
        phases=phases,
    )


def test_redistribution_preserves_total(sample_plan):
    result = redistribute_sdlc_duration(
        sample_plan,
        phase_name="Testing",
        new_duration_weeks=6,
    )

    assert result.total_duration_weeks == 20

    assert sum(
        phase.estimated_duration_weeks
        for phase in result.phases
    ) == 20

    assert result.phases[3].estimated_duration_weeks == 6


def test_redistribution_preserves_phase_order(sample_plan):
    result = redistribute_sdlc_duration(
        sample_plan,
        phase_name="Implementation",
        new_duration_weeks=8,
    )

    assert [phase.name for phase in result.phases] == [
        phase.name for phase in sample_plan.phases
    ]


def test_all_phase_durations_remain_positive(sample_plan):
    result = redistribute_sdlc_duration(
        sample_plan,
        phase_name="Testing",
        new_duration_weeks=12,
    )

    assert all(
        phase.estimated_duration_weeks >= 1
        for phase in result.phases
    )


def test_invalid_phase_name(sample_plan):
    with pytest.raises(ValueError, match="Phase not found"):
        redistribute_sdlc_duration(
            sample_plan,
            phase_name="Unknown",
            new_duration_weeks=5,
        )


def test_invalid_duration(sample_plan):
    with pytest.raises(ValueError, match="must be positive"):
        redistribute_sdlc_duration(
            sample_plan,
            phase_name="Testing",
            new_duration_weeks=0,
        )


def test_duration_exceeds_available_time(sample_plan):
    with pytest.raises(ValueError, match="Not enough weeks"):
        redistribute_sdlc_duration(
            sample_plan,
            phase_name="Testing",
            new_duration_weeks=18,
        )



def test_redistribution_uses_phase_importance(sample_plan):
    result = redistribute_sdlc_duration(
        sample_plan,
        phase_name="Testing",
        new_duration_weeks=6,
    )

    durations = {
        phase.name: phase.estimated_duration_weeks
        for phase in result.phases
    }

    # Implementation has higher importance and a longer
    # original duration than Deployment.
    assert (
        durations["Implementation"]
        > durations["Deployment"]
    )

    # The user-edited phase keeps its requested duration.
    assert durations["Testing"] == 6

    # The total project duration stays unchanged.
    assert sum(durations.values()) == 20



def test_redistribution_respects_importance_weights(
    sample_plan, monkeypatch
):
    custom_weights = {
        name: 1.0
        for name in SDLC_PHASE_WEIGHTS["Waterfall"]
    }

    # Give Deployment a much higher importance.
    custom_weights["Deployment"] = 100.0

    monkeypatch.setitem(
        SDLC_PHASE_WEIGHTS,
        "Waterfall",
        custom_weights,
    )

    result = redistribute_sdlc_duration(
        sample_plan,
        phase_name="Testing",
        new_duration_weeks=6,
    )

    durations = {
        phase.name: phase.estimated_duration_weeks
        for phase in result.phases
    }

    assert durations["Deployment"] > durations["Implementation"]
    assert durations["Testing"] == 6
    assert sum(durations.values()) == 20




def test_redistribute_sdlc_api(sample_plan):
    response = client.post(
        "/api/ai/sdlc/redistribute",
        json={
            "plan": sample_plan.model_dump(mode="json"),
            "phase_name": "Testing",
            "new_duration_weeks": 6,
        },
    )

    print("\nAPI RESPONSE:", response.json())

    assert response.status_code == 200

    result = response.json()

    
    assert result["totalDurationWeeks"] == 20

    durations = {
        phase["name"]: phase["estimatedDurationWeeks"]
        for phase in result["phases"]
    }

    assert durations["Testing"] == 6
    assert sum(durations.values()) == 20



def test_redistribute_api_rejects_unknown_phase(sample_plan):
    response = client.post(
        "/api/ai/sdlc/redistribute",
        json={
            "plan": sample_plan.model_dump(mode="json"),
            "phase_name": "Unknown Phase",
            "new_duration_weeks": 5,
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_SDLC_DURATION"


def test_redistribute_api_rejects_zero_duration(sample_plan):
    response = client.post(
        "/api/ai/sdlc/redistribute",
        json={
            "plan": sample_plan.model_dump(mode="json"),
            "phase_name": "Testing",
            "new_duration_weeks": 0,
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_INPUT"



def sample_srs_data():
    return {
        "introduction": {
            "purpose": "Manage library operations",
            "scope": "Books and borrowing",
            "definitionsAndAcronyms": [],
        },
        "overallDescription": {
            "productPerspective": "Web application",
            "userClasses": ["Librarian"],
            "operatingEnvironment": "Web browser",
            "designAndImplementationConstraints": [],
            "assumptionsAndDependencies": [],
        },
        "systemWorkflowAndStateRules": {
            "mainWorkflow": ["Manage books"],
            "stageApprovalAndDependencyRules": [],
            "projectStatus": [],
        },
        "functionalRequirements": [
            {
                "id": "FR-001",
                "description": "Manage books",
            }
        ],
        "nonFunctionalRequirements": [],
        "dataRequirements": {
            "mainDataEntities": ["Book"],
            "dataOwnershipAndDeletion": "Managed by librarian",
        },
        "businessRules": [],
        "externalInterfaceRequirements": {
            "userInterface": ["Web interface"],
            "aiServiceInterface": "Not required",
            "emailInterface": "Not required",
            "exportInterface": "Not required",
        },
        "acceptanceCriteria": [],
        "implementationDecisions": [],
    }


def test_generate_sdlc_api(sample_plan):
    with patch(
        "main.generate_sdlc_plan",
        return_value=sample_plan,
    ) as mock_generate:

        response = client.post(
            "/api/ai/sdlc/generate",
            json={
                "projectName": "Library Management System",
                "srs": sample_srs_data(),
                "approvedMethodology": "Waterfall",
                "projectDurationWeeks": 20,
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["methodology"] == "Waterfall"
    assert result["totalDurationWeeks"] == 20
    assert len(result["phases"]) == 6

    mock_generate.assert_called_once()



def test_generate_sdlc_rejects_wrong_phase_order(
    sample_plan, monkeypatch
):
    import gemini_service

    # Create a valid SRS input.
    from schemas import SRSResult

    srs = SRSResult.model_validate(sample_srs_data())

    data = SDLCPlanInput(
        project_name="Library Management System",
        srs=srs,
        approved_methodology="Waterfall",
        project_duration_weeks=20,
    )

    # Simulate Gemini returning phases in the wrong order.
    wrong_plan = sample_plan.model_copy(
        update={
            "phases": list(reversed(sample_plan.phases))
        }
    )

    fake_response = MagicMock()
    fake_response.text = wrong_plan.model_dump_json(
        by_alias=True
    )

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client,
    )

    with pytest.raises(
        ValueError,
        match="required methodology structure",
    ):
        generate_sdlc_plan(data)



def test_generate_sdlc_rejects_incorrect_duration_total(
    sample_plan, monkeypatch
):
    import gemini_service
    from schemas import SRSResult

    srs = SRSResult.model_validate(sample_srs_data())

    data = SDLCPlanInput(
        project_name="Library Management System",
        srs=srs,
        approved_methodology="Waterfall",
        project_duration_weeks=20,
    )

    # Gemini returns valid phases, but their durations
    # add up to 22 weeks instead of 20.
    wrong_phases = [
        phase.model_copy(deep=True)
        for phase in sample_plan.phases
    ]

    wrong_phases[3] = wrong_phases[3].model_copy(
        update={"estimated_duration_weeks": 6}
    )

    wrong_plan = sample_plan.model_copy(
        update={"phases": wrong_phases}
    )

    fake_response = MagicMock()
    fake_response.text = wrong_plan.model_dump_json(
        by_alias=True
    )

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client,
    )

    with pytest.raises(
        ValueError,
        match="phase durations do not match total duration",
    ):
        generate_sdlc_plan(data)



def test_generate_sdlc_rejects_wrong_requested_duration(
    sample_plan, monkeypatch
):
    import gemini_service
    from schemas import SRSResult

    srs = SRSResult.model_validate(sample_srs_data())

    data = SDLCPlanInput(
        project_name="Library Management System",
        srs=srs,
        approved_methodology="Waterfall",
        project_duration_weeks=20,
    )

    # Gemini returns 24 weeks instead of the requested 20.
    wrong_phases = [
        phase.model_copy(deep=True)
        for phase in sample_plan.phases
    ]

    wrong_phases[2] = wrong_phases[2].model_copy(
        update={"estimated_duration_weeks": 10}
    )

    wrong_plan = sample_plan.model_copy(
        update={
            "total_duration_weeks": 24,
            "phases": wrong_phases,
        }
    )

    fake_response = MagicMock()
    fake_response.text = wrong_plan.model_dump_json(
        by_alias=True
    )

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client,
    )

    with pytest.raises(
        ValueError,
        match="does not match requested duration",
    ):
        generate_sdlc_plan(data)



def test_generate_sdlc_estimates_duration_when_not_provided(
    sample_plan, monkeypatch
):
    import gemini_service
    from schemas import SRSResult

    srs = SRSResult.model_validate(sample_srs_data())

    data = SDLCPlanInput(
        project_name="Library Management System",
        srs=srs,
        approved_methodology="Waterfall",
        project_duration_weeks=None,
    )

    sample_plan = sample_plan.model_copy(
        update={
            "phase_importance_weights": {
                "Requirements Analysis": 1.2,
                "System Design": 1.2,
                "Implementation": 2.0,
                "Testing": 1.6,
                "Deployment": 0.8,
                "Maintenance": 1.0,
            }
        }
    )
    # Simulate Gemini estimating a 20-week plan.
    fake_response = MagicMock()
    fake_response.text = sample_plan.model_dump_json(
        by_alias=True
    )

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client,
    )

    result = generate_sdlc_plan(data)

    assert result.total_duration_weeks == 20
    assert sum(
        phase.estimated_duration_weeks
        for phase in result.phases
    ) == 20

    fake_client.models.generate_content.assert_called_once()



def test_generate_sdlc_rejects_wrong_methodology(
    sample_plan, monkeypatch
):
    import gemini_service
    from schemas import SRSResult

    srs = SRSResult.model_validate(sample_srs_data())

    data = SDLCPlanInput(
        project_name="Library Management System",
        srs=srs,
        approved_methodology="Waterfall",
        project_duration_weeks=20,
    )

    # Gemini returns Agile instead of Waterfall.
    wrong_plan = sample_plan.model_copy(
        update={"methodology": "Agile"}
    )

    fake_response = MagicMock()
    fake_response.text = wrong_plan.model_dump_json(
        by_alias=True
    )

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client,
    )

    with pytest.raises(ValueError):
        generate_sdlc_plan(data)



def test_generate_sdlc_rejects_empty_gemini_response(
    monkeypatch
):
    import gemini_service
    from schemas import SRSResult

    srs = SRSResult.model_validate(sample_srs_data())

    data = SDLCPlanInput(
        project_name="Library Management System",
        srs=srs,
        approved_methodology="Waterfall",
        project_duration_weeks=20,
    )

    fake_response = MagicMock()
    fake_response.text = None

    fake_client = MagicMock()
    fake_client.models.generate_content.return_value = (
        fake_response
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client,
    )

    with pytest.raises(
        ValueError,
        match="Gemini returned an empty response",
    ):
        generate_sdlc_plan(data)


def test_generate_sdlc_api_hides_internal_errors():
    with patch(
        "main.generate_sdlc_plan",
        side_effect=RuntimeError("SECRET_GEMINI_API_KEY"),
    ):
        response = client.post(
            "/api/ai/sdlc/generate",
            json={
                "projectName": "Library Management System",
                "srs": sample_srs_data(),
                "approvedMethodology": "Waterfall",
                "projectDurationWeeks": 20,
            },
        )

    assert response.status_code == 500

    response_text = response.text

    assert "SECRET_GEMINI_API_KEY" not in response_text
    assert "Failed to generate SDLC plan." in response_text



def test_redistribution_uses_project_specific_weights(
    sample_plan,
):
    from gemini_service import redistribute_sdlc_duration

    # Two plans with the same phases and durations,
    # but different project-specific priorities.
    testing_priority_plan = sample_plan.model_copy(
        update={
            "phase_importance_weights": {
                "Requirements Analysis": 1.0,
                "System Design": 1.0,
                "Implementation": 1.0,
                "Testing": 10.0,
                "Deployment": 1.0,
                "Maintenance": 1.0,
            }
        }
    )

    implementation_priority_plan = sample_plan.model_copy(
        update={
            "phase_importance_weights": {
                "Requirements Analysis": 1.0,
                "System Design": 1.0,
                "Implementation": 10.0,
                "Testing": 1.0,
                "Deployment": 1.0,
                "Maintenance": 1.0,
            }
        }
    )

    testing_result = redistribute_sdlc_duration(
        testing_priority_plan,
        phase_name="Deployment",
        new_duration_weeks=5,
    )

    implementation_result = redistribute_sdlc_duration(
        implementation_priority_plan,
        phase_name="Deployment",
        new_duration_weeks=5,
    )

    testing_durations = {
        phase.name: phase.estimated_duration_weeks
        for phase in testing_result.phases
    }

    implementation_durations = {
        phase.name: phase.estimated_duration_weeks
        for phase in implementation_result.phases
    }

    # Higher testing priority should allocate more
    # weeks to Testing.
    assert (
        testing_durations["Testing"]
        > implementation_durations["Testing"]
    )

    # Higher implementation priority should allocate
    # more weeks to Implementation.
    assert (
        implementation_durations["Implementation"]
        > testing_durations["Implementation"]
    )

    # Both plans must preserve the original total.
    assert sum(testing_durations.values()) == 20
    assert sum(implementation_durations.values()) == 20



@pytest.mark.parametrize(
    "invalid_weights",
    [
        {"Testing": 2.0},
        {
            "Requirements Analysis": 1.0,
            "System Design": 1.0,
            "Implementation": 1.0,
            "Testing": 0.0,
            "Deployment": 1.0,
            "Maintenance": 1.0,
        },
        {
            "Requirements Analysis": 1.0,
            "System Design": 1.0,
            "Implementation": float("inf"),
            "Testing": 1.0,
            "Deployment": 1.0,
            "Maintenance": 1.0,
        },
    ],
)
def test_redistribution_rejects_invalid_project_weights(
    sample_plan, invalid_weights
):
    invalid_plan = sample_plan.model_copy(
        update={
            "phase_importance_weights": invalid_weights
        }
    )

    with pytest.raises(ValueError):
        redistribute_sdlc_duration(
            invalid_plan,
            phase_name="Deployment",
            new_duration_weeks=5,
        )



def test_redistribute_api_rejects_invalid_project_weights(
    sample_plan,
):
    invalid_plan = sample_plan.model_copy(
        update={
            "phase_importance_weights": {
                "Testing": 2.0
            }
        }
    )

    response = client.post(
        "/api/ai/sdlc/redistribute",
        json={
            "plan": invalid_plan.model_dump(
                by_alias=True
            ),
            "phaseName": "Deployment",
            "newDurationWeeks": 5,
        },
    )

    assert response.status_code == 400

    result = response.json()

    assert result["code"] == "INVALID_SDLC_DURATION"
    assert "Invalid project-specific SDLC phase weights" in (
        result["message"]
    )
