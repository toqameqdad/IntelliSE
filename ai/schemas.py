
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