
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class ProjectInput(BaseSchema):
    project_name: str = Field(min_length=1)
    project_description: str = Field(min_length=20)


class Requirement(BaseSchema):
    type: Literal["functional", "non_functional"]
    description: str = Field(min_length=1)
    priority: Literal["must", "should"]
    rationale: str = Field(min_length=1)
    source: Literal["explicit", "inferred"]


class RequirementsResult(BaseSchema):
    functional_requirements: list[Requirement]
    non_functional_requirements: list[Requirement]

    @model_validator(mode="after")
    def validate_requirements(self):
        for requirement in self.functional_requirements:
            if requirement.type != "functional":
                raise ValueError(
                    "Functional requirements must have type 'functional'"
                )

        for requirement in self.non_functional_requirements:
            if requirement.type != "non_functional":
                raise ValueError(
                    "Non-functional requirements must have type 'non_functional'"
                )

        descriptions = [
            " ".join(item.description.casefold().split())
            for item in (
                self.functional_requirements
                + self.non_functional_requirements
            )
        ]

        if len(descriptions) != len(set(descriptions)):
            raise ValueError("Duplicate requirements detected")

        return self


class ClarificationQuestion(BaseSchema):
    question: str
    reason: str
    related_area: Literal[
        "functionality",
        "users",
        "business_rules",
        "data",
        "platform",
        "security",
        "performance",
        "constraints",
    ]


class ClarificationResult(BaseSchema):
    needs_clarification: bool
    questions: list[ClarificationQuestion]


class ClarificationAnswer(BaseSchema):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class ClarificationAnswersInput(ProjectInput):
    answers: list[ClarificationAnswer] = Field(min_length=1)


class RequirementsGenerationInput(ProjectInput):
    answers: list[ClarificationAnswer] = Field(default_factory=list)



class SRSInput(BaseSchema):
    project_name: str = Field(min_length=1)
    project_description: str = Field(min_length=20)
    functional_requirements: list[Requirement] = Field(min_length=1)
    non_functional_requirements: list[Requirement] = Field(min_length=1)


class SRSIntroduction(BaseSchema):
    purpose: str
    scope: str
    definitions_and_acronyms: list[str]


class SRSOverallDescription(BaseSchema):
    product_perspective: str
    user_classes: list[str]
    operating_environment: str
    design_and_implementation_constraints: list[str]
    assumptions_and_dependencies: list[str]


class SRSWorkflow(BaseSchema):
    main_workflow: list[str]
    stage_approval_and_dependency_rules: list[str]
    project_status: list[str]


class SRSRequirement(BaseSchema):
    id: str
    description: str


class SRSNonFunctionalRequirement(BaseSchema):
    id: str
    category: str
    description: str


class SRSDataRequirements(BaseSchema):
    main_data_entities: list[str]
    data_ownership_and_deletion: str


class SRSExternalInterfaces(BaseSchema):
    user_interface: list[str]
    ai_service_interface: str
    email_interface: str
    export_interface: str


class SRSResult(BaseSchema):
    introduction: SRSIntroduction
    overall_description: SRSOverallDescription
    system_workflow_and_state_rules: SRSWorkflow
    functional_requirements: list[SRSRequirement]
    non_functional_requirements: list[SRSNonFunctionalRequirement]
    data_requirements: SRSDataRequirements
    business_rules: list[str]
    external_interface_requirements: SRSExternalInterfaces
    acceptance_criteria: list[str]
    implementation_decisions: list[str]
