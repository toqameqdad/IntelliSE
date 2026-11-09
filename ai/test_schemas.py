from schemas import ProjectInput, RequirementsResult

project = ProjectInput.model_validate({
    "projectName": "IntelliSE",
    "projectDescription": (
        "An AI-powered system for software requirements "
        "analysis and documentation."
    )
})

print(project)

result = RequirementsResult.model_validate({
    "functionalRequirements": [
        {
            "type": "functional",
            "description": "The system shall generate requirements.",
            "priority": "must",
            "rationale": "This is a core system feature."
        }
    ],
    "nonFunctionalRequirements": [
        {
            "type": "non_functional",
            "description": "The system shall respond within 5 seconds.",
            "priority": "should",
            "rationale": "This improves system performance."
        }
    ]
})

print(result.model_dump(by_alias=True))