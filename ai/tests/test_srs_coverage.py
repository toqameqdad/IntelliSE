"""Tests for SRS requirement coverage and sequential IDs."""

import pytest

from schemas import (
    SRSInput,
    SRSResult,
    SRSRequirement,
    SRSNonFunctionalRequirement,
    validate_srs_coverage,
)


@pytest.fixture
def approved_requirements():
    return SRSInput.model_validate({
        "projectName": "Demo",
        "projectDescription": "A project for managing tasks and reporting progress.",
        "functionalRequirements": [
            {
                "type": "functional",
                "description": "Create tasks",
                "priority": "must",
                "rationale": "Users need to track work",
                "source": "explicit",
            },
            {
                "type": "functional",
                "description": "Assign tasks",
                "priority": "should",
                "rationale": "Users need ownership",
                "source": "explicit",
            },
        ],
        "nonFunctionalRequirements": [
            {
                "type": "non_functional",
                "description": "Protect task data",
                "priority": "must",
                "rationale": "Data privacy",
                "source": "explicit",
            },
        ],
    })


def srs_with_ids(functional_ids, non_functional_ids):
    # The coverage function reads only the requirement collections.
    return SRSResult.model_construct(
        functional_requirements=[
            SRSRequirement(id=item, description="Approved behavior")
            for item in functional_ids
        ],
        non_functional_requirements=[
            SRSNonFunctionalRequirement(
                id=item, category="security", description="Approved constraint"
            )
            for item in non_functional_ids
        ],
    )


def test_srs_coverage_accepts_expected_counts_and_ids(approved_requirements):
    result = srs_with_ids(["FR-001", "FR-002"], ["NFR-001"])
    assert validate_srs_coverage(approved_requirements, result) is result


@pytest.mark.parametrize(
    "functional_ids, non_functional_ids",
    [
        (["FR-001"], ["NFR-001"]),
        (["FR-001", "FR-002", "FR-003"], ["NFR-001"]),
        (["FR-001", "FR-001"], ["NFR-001"]),
        (["FR-002", "FR-001"], ["NFR-001"]),
        (["FR-001", "FR-003"], ["NFR-001"]),
        (["FR-001", "FR-002"], []),
        (["FR-001", "FR-002"], ["NFR-002"]),
    ],
)
def test_srs_coverage_rejects_invalid_ids(
    approved_requirements, functional_ids, non_functional_ids
):
    result = srs_with_ids(functional_ids, non_functional_ids)
    with pytest.raises(ValueError, match="requirements are missing, extra, or out of order"):
        validate_srs_coverage(approved_requirements, result)
