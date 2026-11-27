import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas import (
    ClarificationAnswersInput,
    ClarificationResult,
    ContextDiagramResult,
    ProjectInput,
    RequirementsGenerationInput,
    RequirementsResult,
    SRSInput,
    SRSResult,
    UseCaseDiagramResult,
    ActivityDiagramResult,
    ObjectDiagramResult,
    MethodologyInput,
    MethodologyRecommendationResult,
    MethodologyCompatibilityInput,
    MethodologyCompatibilityResult,
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_requirements(
    data: RequirementsGenerationInput,
) -> RequirementsResult:

    answers_text = "\n".join(
        f"Question: {item.question}\nAnswer: {item.answer}"
        for item in data.answers
    ) or "No clarification answers were provided."

    prompt = f"""
    You are a professional software requirements analyst.

    Analyze the following software project:

    Project Name: {data.project_name}

    Project Description:
    {data.project_description}

    Clarification Questions and User Answers:
    {answers_text}

    Generate functional and non-functional requirements.

    Rules:
    - Generate requirements based on the original project description
      and the clarification answers.
    - Treat clear user answers as additional project information.
    - Do not ignore or contradict the user's clarification answers.
    - Do not invent unsupported project features.
    - Each requirement must have a clear and specific description.
    - Assign a priority: must or should.
    - Explain the reason behind each requirement.
    - Keep functional and non-functional requirements separate.
    - Do not generate requirement IDs.
    - Avoid duplicate or overlapping requirements.
    - For every requirement, identify its source.
    - Use "explicit" when the requirement is directly supported
      by the project description or clarification answers.
    - Use "inferred" when the requirement is reasonably inferred
      from the project's context but was not explicitly mentioned.
    - Do not present inferred requirements as confirmed user decisions.
    - Avoid unnecessary assumptions and unsupported features.
    - Inferred requirements should only include essential or strongly justified
      assumptions, not optional features or arbitrary design decisions.
    - Do not assume that common features or best practices
      are required unless they are explicitly requested
      or essential for the project to function.
    - Do not generate optional usability enhancements
      as requirements unless supported by the project context.
    - Non-functional requirements must describe quality attributes
      or operational constraints, such as security, performance,
      usability, reliability, or accessibility.
    - Do not classify application features, platforms, or
      technology types as non-functional requirements.
    - Avoid generating duplicate requirements that describe
      the same system behavior.
    - Functional requirements describe specific system behaviors
      or actions that users can perform.
    - Non-functional requirements describe quality attributes
      or constraints on how the system operates.
    - Security-related access restrictions may be classified
      as non-functional requirements when they express
      authorization or data protection constraints.
    - Avoid duplicating the same behavior across functional
      and non-functional requirements.
        """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                RequirementsResult.model_json_schema(by_alias=True)
            ),
            temperature=0.2,
            max_output_tokens=4000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return RequirementsResult.model_validate_json(response.text)

def clean_schema(schema):
    if isinstance(schema, dict):
        schema.pop("additionalProperties", None)
        schema.pop("additional_properties", None)

        for value in schema.values():
            clean_schema(value)

    elif isinstance(schema, list):
        for item in schema:
            clean_schema(item)

    return schema


def analyze_project(project: ProjectInput) -> ClarificationResult:
    prompt = f"""
    You are a professional software requirements analyst.

    Analyze the following software project description:

    Project Name: {project.project_name}
    Project Description: {project.project_description}

    Your task is to determine whether the provided information
    is sufficient to generate accurate software requirements.

    Rules:
    - Identify only essential missing, ambiguous, or conflicting information.
    - Ask questions only when missing information prevents
      accurate understanding of the project's core functionality.
    - Do not ask about optional features or enhancements.
    - Do not ask about technical implementation details
      such as authentication methods, session management,
      database technology, or API design.
    - Do not ask about details that can reasonably be
      proposed as suggestions during requirements generation.
    - Do not assume that every unspecified detail requires clarification.
    - Focus on understanding what the system should do,
      who will use it, and its main purpose.
    - Ask specific and concise questions.
    - Avoid asking multiple questions that cover the same topic.
    - If the project description is sufficiently clear
      to generate initial requirements, return:
      needsClarification = false and an empty questions list.
    - Do not generate functional or non-functional requirements.

    Return the result using the required JSON structure.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                ClarificationResult.model_json_schema(by_alias=True)
            ),
            temperature=0.2,
            max_output_tokens=2000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return ClarificationResult.model_validate_json(response.text)


def reanalyze_project(
    data: ClarificationAnswersInput,
) -> ClarificationResult:

    answers_text = "\n".join(
        f"Question: {item.question}\nAnswer: {item.answer}"
        for item in data.answers
    )

    prompt = f"""
    You are a professional software requirements analyst.

    Analyze the project using the original description
    and the user's clarification answers.

    Project Name: {data.project_name}

    Original Project Description:
    {data.project_description}

    Clarification Questions and User Answers:
    {answers_text}

    Rules:
    - Consider both the original description and user answers.
    - Treat clear user answers as additional project information.
    - Do not ignore or contradict the user's answers.
    - Identify only essential missing, ambiguous, or conflicting information.
    - Do not repeat questions that have already been answered clearly.
    - If an answer conflicts with the original description,
      ask a question to resolve the conflict.
    - Do not ask about optional features or technical implementation details.
    - If the available information is sufficient,
      return needsClarification = false and an empty questions list.
    - Do not generate functional or non-functional requirements.

    Return the result using the required JSON structure.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                ClarificationResult.model_json_schema(by_alias=True)
            ),
            temperature=0.2,
            max_output_tokens=2000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return ClarificationResult.model_validate_json(response.text)



def generate_srs(data: SRSInput) -> SRSResult:
    functional_requirements = "\n".join(
        f"- {item.description}"
        for item in data.functional_requirements
    )

    non_functional_requirements = "\n".join(
        f"- {item.description} (Priority: {item.priority})"
        for item in data.non_functional_requirements
    )

        
    prompt = f"""
    You are a professional software requirements analyst.

    STANDARDS AND SRS GUIDELINES:

    - Use ISO/IEC/IEEE 29148:2018 as the primary reference
    for requirements engineering principles and SRS quality.

    - Use the traditional IEEE 830-style SRS outline as a
    structural reference, while following the exact
    10-section structure defined in the output schema.

    - Ensure requirements are clear, unambiguous, complete,
    consistent, feasible, verifiable, and traceable.

    - Each requirement must express one clear, testable
    system behavior or quality constraint.

    - Avoid vague terms such as "fast", "user-friendly",
    or "secure" unless supported by measurable criteria.

    - Maintain consistency between functional requirements,
    non-functional requirements, business rules,
    workflows, and acceptance criteria.

    - Do not claim formal compliance or certification
    with either standard.

    PROJECT INFORMATION:

    Project Name:
    {data.project_name}

    Project Description:
    {data.project_description}

    Approved Functional Requirements:
    {functional_requirements}

    Approved Non-Functional Requirements:
    {non_functional_requirements}

    TASK:

    Generate a complete Software Requirements Specification
    (SRS) for the project using the following sections:

    1. Introduction:
    - Purpose
    - Scope
    - Definitions and Acronyms

    2. Overall Description:
    - Product Perspective
    - User Classes
    - Operating Environment
    - Design and Implementation Constraints
    - Assumptions and Dependencies

    3. System Workflow and State Rules:
    - Main Workflow
    - Stage Approval and Dependency Rules
    - Project Status

    4. Functional Requirements

    5. Non-Functional Requirements

    6. Data Requirements:
    - Main Data Entities
    - Data Ownership and Deletion

    7. Business Rules

    8. External Interface Requirements:
    - User Interface
    - AI Service Interface
    - Email Interface
    - Export Interface

    9. Acceptance Criteria

    10. Items Reserved for Implementation Decisions

    INFORMATION ACCURACY AND REASONING RULES:

    1. Treat the Project Description as the source of
    project context, scope, and explicitly mentioned
    capabilities.

    2. Treat the Approved Functional and Non-Functional
    Requirements as authoritative requirements.
    Preserve their meaning, priority, and intended behavior.

    3. Do not remove, contradict, weaken, or replace
    approved requirements.

    4. Distinguish between three types of information
    during generation:

    - Explicit: Directly stated in the input.
    - Derived: A reasonable conclusion that follows
        logically from the provided information.
    - Unknown: Information that cannot be established
        from the available input.

    5. Use explicit and logically derived information
    when appropriate. Do not restrict the SRS to
    copying the input word for word.

    6. Derived information must:
    - Have a clear basis in the provided input.
    - Be necessary or useful for explaining the system.
    - Never introduce new features, business policies,
        technical decisions, or unsupported constraints.
    - Never be presented as an explicitly approved decision.

    7. Do not invent technologies, platforms, integrations,
    user roles, permissions, numerical targets,
    workflows, or implementation decisions.

    8. If information is unknown, use "Not specified".
    Do not fill gaps with assumptions presented as facts.

    9. When the Project Description and approved
    requirements provide conflicting information,
    preserve the approved requirement and do not
    silently resolve or modify the conflict.

    REQUIREMENT PRESERVATION AND CONSISTENCY:

    - Preserve every approved functional and
    non-functional requirement.

    - Do not unnecessarily split one requirement into
    multiple requirements or combine unrelated requirements.

    - You may improve wording for clarity, but must
    preserve the original meaning and scope.

    - Do not add new functional or non-functional
    requirements unless they are explicitly supported
    by the provided project information.

    - Avoid duplicating the same requirement across
    different sections unless the repetition serves
    a necessary documentation purpose.

    - Ensure that business rules and workflow steps
    are derived from the provided project information.

    - Identify user classes and data entities from
    explicitly stated or logically supported information.

    WORKFLOW AND ACCEPTANCE CRITERIA:

    - Derive workflow steps and state transitions
    from the approved requirements and project description.

    - Do not invent approval stages, status values,
    dependencies, or conditions that are not supported
    by the input.

    - Each acceptance criterion must be specific,
    observable, and verifiable.

    - Where possible, express acceptance criteria
    as measurable conditions or expected system behavior.

    - Acceptance criteria must cover the relevant
    functional and non-functional requirements.

    - Do not introduce new functionality through
    acceptance criteria.

    NON-FUNCTIONAL REQUIREMENTS:

    - Preserve all provided measurable values and constraints.

    - Do not invent performance targets, availability
    percentages, capacity limits, or security standards.

    - Do not turn vague quality expectations into
    specific numerical requirements without evidence.

    - Where a requirement cannot be objectively verified
    because necessary details are missing, preserve
    its meaning and avoid inventing measurement criteria.

    IDENTIFIERS AND OUTPUT:

    - Assign sequential IDs to functional requirements:
    FR-001, FR-002, and so on.

    - Assign sequential IDs to non-functional requirements:
    NFR-001, NFR-002, and so on.

    - Each functional requirement must contain an ID
    and description.

    - Each non-functional requirement must contain
    an ID, category, and description.

    - Keep the SRS professional, clear, specific,
    and consistent.

    - Avoid unnecessary repetition and generic descriptions.

    - Do not generate content for IntelliSE unless
    IntelliSE is the actual project being described.

    - Return all required sections using the provided
    JSON schema.

    FINAL VALIDATION BEFORE OUTPUT:

    Before returning the SRS, internally verify that:

    1. All approved requirements are preserved.
    2. No unsupported features or technical decisions
    have been introduced.
    3. Explicit information is not incorrectly marked
    as unknown.
    4. Derived information is logically supported.
    5. Workflows and business rules are consistent
    with the requirements.
    6. Acceptance criteria are testable and do not
    introduce new requirements.
    7. Requirement IDs are sequential and unique.
    8. All required sections and fields are populated.
    9. The output follows the provided JSON schema.

    Return only valid JSON matching the provided schema.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                SRSResult.model_json_schema(by_alias=True)
            ),
            temperature=0.2,
            max_output_tokens=6000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return SRSResult.model_validate_json(response.text)



def recommend_methodology(
    data: MethodologyInput,
) -> MethodologyRecommendationResult:

    srs_content = data.srs.model_dump_json(
        by_alias=True,
        exclude_none=True,
    )

    prompt = f"""
    You are a professional software development methodology expert.

    Analyze the following software project:

    Project Name:
    {data.project_name}

    Approved SRS:
    {srs_content}

    Your task is to recommend the most suitable development
    methodology for this project.

    Available methodologies:
    - Agile
    - Waterfall
    - Spiral

    Consider the following project characteristics:
    - Clarity and stability of requirements.
    - Likelihood of changing requirements.
    - Project complexity.
    - Technical and project risks.
    - Need for iterative development and user feedback.
    - Need for a structured and sequential development process.

    Rules:
    - Select exactly one methodology from the three available options.
    - Base your recommendation on the provided SRS.
    - Consider the actual project characteristics, not general preferences.
    - Do not assume project characteristics that are not supported
      by the SRS.
    - Do not recommend a methodology simply because it is popular.
    - Explain clearly why the selected methodology fits the project.
    - Do not generate an SDLC plan or project timeline.
    - Return only valid JSON matching the provided schema.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                MethodologyRecommendationResult.model_json_schema(
                    by_alias=True
                )
            ),
            temperature=0.2,
            max_output_tokens=1500,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return MethodologyRecommendationResult.model_validate_json(
        response.text
    )



def analyze_methodology_compatibility(
    data: MethodologyCompatibilityInput,
) -> MethodologyCompatibilityResult:

    supported_methodologies = {"agile", "waterfall", "spiral"}

    is_custom_methodology = (
        data.selected_methodology.strip().casefold()
        not in supported_methodologies
    )

    prompt = f"""
    You are a professional software development methodology expert.

    Analyze whether the user's selected development methodology
    is suitable for the following project.

    Project Name:
    {data.project_name}

    Approved SRS:
    {data.srs.model_dump_json(by_alias=True, indent=2)}

    Originally Recommended Methodology:
    {data.recommended_methodology}

    User Selected Methodology:
    {data.selected_methodology}

    Your task is to evaluate the compatibility of the selected
    methodology with the project's characteristics.

    Consider:
    - Requirements clarity and stability.
    - Expected changes during development.
    - Project complexity.
    - Technical and project risks.
    - Need for iterative feedback.
    - Suitability of the methodology's development approach.

    Rules:
    - Evaluate the selected methodology based on the project,
      not merely because it differs from the recommendation.
    - Do not automatically classify a different methodology
      as incompatible.
    - Use "compatible" when the selected methodology is suitable.
    - Use "potentially_incompatible" when important project
      characteristics conflict with the selected methodology.
    - Explain the reasons behind your assessment.
    - If potentially incompatible, provide a clear warning
      explaining the concern.
    - Do not invent project characteristics.
    - Do not generate an SDLC plan or project timeline.
    - Return only valid JSON matching the provided schema.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                MethodologyCompatibilityResult.model_json_schema(
                    by_alias=True
                )
            ),
            temperature=0.2,
            max_output_tokens=1500,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    result = MethodologyCompatibilityResult.model_validate_json(
        response.text
    )

    if is_custom_methodology:
        support_warning = (
            "This methodology is not one of IntelliSE's built-in "
            "options (Agile, Waterfall, Spiral), so it is not "
            "fully supported by the system."
        )

        warning = result.warning

        if warning:
            warning = f"{warning.rstrip()} {support_warning}"
        else:
            warning = support_warning

        result = result.model_copy(
            update={"warning": warning}
        )

    return result


CONTEXT_DIAGRAM_PROMPT = """
You are a professional software engineer specialized in
System Context Diagram generation.

Your task is to generate a System Context Diagram based
strictly on the provided latest approved SRS.

GENERAL RULES:

- Identify the main system being described.
- Identify external entities that interact directly with the system.
- Include only entities supported by the SRS.
- Identify the main data flows between the system and each
  external entity.
- Every data flow must connect the main system to an external entity.
- Specify the direction of each data flow correctly.
- Use short, clear, and specific labels describing the actual
  information being exchanged.
- Separate input and output flows when they represent different
  types of information.
- Do not combine unrelated operations into one vague data flow.
- Do not omit important interactions just to reduce the number
  of data flows.
- Group related interactions only when they have the same source,
  target, and direction.
- Prefer completeness over excessive simplification.
- A context diagram should represent the system's major external
  interactions without listing every individual functional requirement.

EXTERNAL ENTITIES:

- Identify distinct user classes separately when the SRS defines
  different roles or access levels.
- Do not merge different user classes into one generic User entity.
- Include external services only when the SRS explicitly identifies
  them or clearly describes their direct interaction with the system.
- Do not include internal system components, databases, or modules
  as external entities.
- Do not infer external integrations from general functional
  requirements.
- For example, do not assume a Payment Gateway, Email Service,
  SMS Service, or another external service unless supported by the SRS.
- Do not invent users, external systems, integrations, or data flows.

DATA FLOW SPECIFICITY:

- Use labels that identify the actual information or requests
  being exchanged.
- Avoid vague labels such as:
  "System Data", "Information", "Data", "User Data",
  "Admin Management Commands", "AI Outputs",
  and "Dashboard Information".
- Include the main categories of interaction whenever supported
  by the SRS, such as:
  authentication, project data submission, clarification answers,
  editing, review, approval, administrative operations,
  AI generation requests, generated outputs, and export requests.
- Do not list every individual action as a separate flow if
  related actions can be grouped clearly.
- However, do not group unrelated interactions under generic labels.
- Make sure each label communicates what is being sent,
  not merely the general purpose of the interaction.

EXTERNAL SERVICE INTERACTIONS:

- For an external AI service, include:
  * System to AI Service: relevant input data, clarification answers,
    and generation or analysis requests described in the SRS.
  * AI Service to System: generated outputs, analysis findings,
    clarification questions, and other supported results.
- For an external email service, describe the actual email requests
  or notification requests sent by the system.
- Do not represent email content as a response from the email
  service unless the SRS explicitly describes such a response.
- Apply these rules only when the corresponding external service
  is supported by the SRS.
- Do not assume that an external service sends a response unless
  this is explicitly supported.

AMBIGUITY AND VALIDATION:

- Do not turn ambiguous requirements into confirmed data flows.
- If a requirement uses uncertain wording such as "may",
  do not treat the described behavior as mandatory.
- If an entity or interaction is possible but not explicitly
  supported by the SRS, do not include it in the diagram.
- Instead, add a warning explaining the missing information.
- Distinguish explicitly stated information from assumptions.
- Never present assumptions as confirmed facts.
- Do not include implementation details.
- If information is insufficient, include a warning explaining
  what is missing.
- Distinguish between navigation and actual data exchange.
- Do not create a data flow for simple page navigation unless
  it represents a meaningful request or interaction with the system.
- Do not generate use cases, activity diagrams, or object diagrams.


CRITICAL CONTEXT DIAGRAM STRUCTURE:

- The main system has the reserved ID "system".
- Every data flow MUST have the main system as either
  its source or its target.
- The only allowed flow directions are:
  * External Entity -> system
  * system -> External Entity
- NEVER create a flow directly between two external entities.
- NEVER create a flow between two external entities,
  even if they communicate with each other through an integration.
- All communication between external entities must be represented
  as two separate flows through the main system, but only when
  supported by the SRS.

VALID EXAMPLES:
- user -> system
- system -> user
- system -> ai_service
- ai_service -> system

INVALID EXAMPLES:
- user -> ai_service
- ai_service -> email_service
- administrator -> user

Before returning the JSON, verify every data flow:
- Its source or target must be "system".
- Its other endpoint must be a declared external entity.
- No flow may connect two external entities directly.

If a flow violates these rules, correct it before returning
the final JSON.


LATEST APPROVED SRS:

{srs_content}

Return only valid JSON matching the provided schema.
"""


def generate_context_diagram(srs_content: str) -> ContextDiagramResult:
    if not srs_content.strip():
        raise ValueError("SRS content cannot be empty")

    prompt = CONTEXT_DIAGRAM_PROMPT.format(
        srs_content=srs_content
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                ContextDiagramResult.model_json_schema(by_alias=True)
            ),
            temperature=0.2,
            max_output_tokens=3000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return ContextDiagramResult.model_validate_json(response.text)




USE_CASE_DIAGRAM_PROMPT = """
You are a professional software engineer specialized in
UML Use Case Diagram generation.

Your task is to generate a UML Use Case Diagram based
strictly on the provided Software Requirements Specification (SRS).

The SRS may describe any type of software system.
You must analyze the actual content of the provided SRS
and generate a diagram specific to that system.

GENERAL RULES:

- Use only information explicitly supported by the SRS.
- Do not assume the project is IntelliSE or any other specific system.
- Do not reuse actors, use cases, or functionality from previous examples.
- Do not introduce predefined actors or use cases.
- Understand the system's purpose, scope, users, and functionality
  before generating the diagram.
- Represent the system's functionality from the perspective
  of the actors who interact with it.
- Use clear, concise, verb-based use case names.
- Each use case must represent a meaningful system function.
- Do not represent internal technical processes as use cases.
- Do not include implementation details.
- Avoid duplicate or overlapping use cases.
- Do not create a separate use case for every minor action.
- Group closely related actions when appropriate.
- Preserve meaningful distinctions between different actors and roles.

ACTOR IDENTIFICATION:

- Identify all human actors explicitly mentioned or clearly
  supported by the SRS.
- Identify external systems only when the SRS explicitly
  describes their interaction with the system.
- Give each actor a meaningful name and a short description.
- Use actor_type "human" for human users.
- Use actor_type "external_system" for external systems.
- Do not invent actors based on assumptions.
- Do not merge actors whose responsibilities or permissions
  are different according to the SRS.

USE CASE IDENTIFICATION:

- Derive use cases from the functional requirements and
  workflows described in the SRS.
- Include the main functions that actors can perform.
- Include account, management, or administrative functions
  only when supported by the SRS.
- Include interactions with external systems only when
  explicitly supported.
- Do not assume common features exist simply because they
  are common in similar applications.
- Do not create use cases for non-functional requirements
  such as security, performance, or usability unless they
  describe an actual actor-interaction function.
- Do not add functionality that is not documented in the SRS.
- Do not omit functional requirements simply because
  they are optional or use words such as "may".
- Represent optional functionality as a use case when
  it describes a meaningful system capability.
- Do not assign actors to use cases based on assumptions.
  Actor associations must be supported by the SRS.
- When the responsible actor is unclear, avoid inventing
  an association.

ACTOR ASSOCIATIONS:

- Associate each use case with the actor or actors that
  directly interact with it.
- Respect the permissions, responsibilities, and access
  restrictions defined in the SRS.
- Do not associate actors with functions they are not
  authorized to perform.
- External systems should only be associated with use cases
  they directly interact with.
- Every use case must reference at least one valid actor ID.
- Do not associate an actor merely because it is indirectly
  involved in a process.

ACTOR ASSOCIATIONS:

- Associate each use case with actors who directly interact
  with that functionality.
- Do not associate actors with internal system operations
  that they do not directly interact with.
- A use case included by another use case may have no
  direct actor association.
- Do not invent actor associations to satisfy a minimum
  number of actors.
- Respect the permissions and responsibilities defined
  in the SRS.
- External systems should only be associated with use cases
  they directly interact with.
- Use an empty actorIds list when a use case represents
  an internal system operation with no direct actor.


INCLUDE AND EXTEND RELATIONSHIPS:

- Use "include" only when one use case necessarily invokes
  another use case as part of its behavior.
- Use "extend" only when optional or conditional behavior
  extends another use case.
- Do not infer relationships from workflow order alone.
- Do not create relationships just to make the diagram
  more detailed.
- If no relationship is clearly justified by the SRS,
  return an empty relationships list.
- Both source and target must reference existing use case IDs.
- A use case cannot have a relationship with itself.
- When a use case requires another use case to execute
  as part of its behavior, use "include".
- The source must be the base use case that includes
  the target use case.
- When optional behavior extends a base use case,
  use "extend".
- The source must be the extending use case, and the
  target must be the base use case.
- Do not use "include" for behavior that is only
  a precondition.


SYSTEM BOUNDARY:

- Use the system name specified in the SRS.
- If the system name is not explicitly provided, infer it
  only when it can be identified clearly from the document.
- Actors represent entities outside the system boundary.
- Use cases represent functions provided inside the
  system boundary.
- Do not represent actors as use cases.

VALIDATION AND ACCURACY:

- Do not invent missing requirements or fill gaps with
  assumptions.
- If information is insufficient to identify a specific
  actor or use case, omit it.
- Return unique IDs for all actors and use cases.
- Use stable, readable IDs within the generated diagram.
- Ensure every actor ID referenced by a use case exists
  in the actors list.
- Empty actorIds lists are allowed for internal system
  operations.
- Ensure every relationship references existing use case IDs.
- Ensure the generated diagram accurately reflects the
  provided SRS, not a generic application template.

LATEST APPROVED SRS:

{srs_content}

Return only valid JSON matching the provided schema.
"""


def generate_use_case_diagram(
    srs_content: str,
) -> UseCaseDiagramResult:

    if not srs_content.strip():
        raise ValueError("SRS content cannot be empty")

    prompt = USE_CASE_DIAGRAM_PROMPT.format(
        srs_content=srs_content
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=clean_schema(
                UseCaseDiagramResult.model_json_schema(by_alias=True)
            ),
            temperature=0.2,
            max_output_tokens=5000,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return UseCaseDiagramResult.model_validate_json(response.text)


ACTIVITY_DIAGRAM_PROMPT = """
You are a professional Software Engineer specialized in UML
Activity Diagrams.

Your task is to analyze the provided Software Requirements
Specification (SRS) and generate a UML Activity Diagram
representing the main workflow of the system.

SRS:
{srs_content}

GENERAL INSTRUCTIONS:

1. Understand the system and identify its main end-to-end workflow.
2. Generate one coherent Activity Diagram representing the
   most important workflow described in the SRS.
3. Base every activity, decision, and transition strictly on
   information supported by the SRS.
4. Do not invent features, actions, business rules, or system
   behavior that are not described in the SRS.
5. Do not convert every functional requirement into a separate
   activity node. Focus on the actual sequence of actions.
6. Use clear and concise English names and descriptions.
7. Do not assume that all system features belong to
   one sequential workflow.
8. Focus on one coherent end-to-end workflow.
   Do not combine independent user activities
   merely because they belong to the same system.
9. Do not assume that activities must occur in a
   specific order unless the SRS explicitly supports
   that sequence.
10. Separate distinct actions when the SRS describes
    them as separate operations, especially when
    they have different outcomes.
11. Ensure that every decision branch represents
    the correct logical outcome of its condition.
    The target of each branch must be consistent
    with the meaning of the condition and the
    subsequent workflow.
12. Keep the activity diagram focused on one clearly
    defined business workflow. Include only activities
    that directly belong to that workflow.
    Do not combine separate workflows unless the SRS
    explicitly defines them as part of the same process.


WORKFLOW SELECTION AND COMPLETENESS:

1. Identify the main workflow based on the functional
   requirements and the relationships between them.

2. Include an activity in the selected workflow when
   it is explicitly required as part of that workflow
   or when the SRS establishes a dependency between it
   and another activity in the workflow.

3. Do not include independent system features merely
   because they are important or commonly used.

4. Do not assume that an activity is a prerequisite
   for another activity unless the SRS explicitly
   establishes that dependency.

5. If an included activity has required validations,
   decisions, or outcomes described in the SRS,
   represent them accurately.

6. Ensure that the selected workflow is complete
   enough to represent its supported start-to-end
   behavior without omitting explicitly required steps.

7. Do not force unrelated functional requirements
   into the selected workflow just to represent
   more system features.


NODE RULES:

1. Every node must have:
   - id: unique identifier.
   - name: short descriptive name.
   - description: explanation of the node.
   - nodeType: one of the allowed node types.
   - partition: responsible actor or system, if identified
     in the SRS; otherwise null.

2. Use only these node types:
   - initial: starting point of the workflow.
   - action: an activity or operation.
   - decision: a point where the workflow branches based on
     a condition.
   - merge: a point where alternative paths come together.
   - fork: a point where parallel activities begin.
   - join: a point where parallel activities synchronize.
   - activity_final: end of the entire workflow.

3. The diagram must contain exactly one initial node and
   at least one activity_final node.

4. Action names should describe activities using verbs.

5. Decision nodes should describe a question or condition.

FLOW RULES:

1. Every flow must connect two existing node IDs.
2. Use source and target to define the direction of each flow.
3. Use condition to describe the condition of a transition.
4. Every decision node must have at least two outgoing flows.
5. Every outgoing flow from a decision node must have a
   meaningful condition, such as "Yes" or "No".
6. Use merge nodes when alternative paths come together.
7. Use fork and join nodes only when the SRS explicitly
   describes parallel activities.
8. Represent loops only when repetition is supported by
   the SRS.
9. Do not create unnecessary nodes or transitions.

WORKFLOW ORDER AND REQUIREMENT CONSISTENCY:

1. Respect all explicit ordering constraints stated in the SRS.
2. If the SRS requires a condition or validation to be
   checked before an action is allowed, place that
   validation before the action.
3. Do not represent an action as completed before
   its required validations or conditions are satisfied.
4. Distinguish between initiating an operation and
   successfully completing it when the SRS makes
   this distinction.
5. Before generating the final JSON, verify that the
   sequence of nodes and flows does not contradict
   any explicit workflow constraints in the SRS.

PARTITIONS:

Use partition to identify the responsible actor or system
for an action when this information is available in the SRS.
Do not invent actors or responsibilities.


PARTITION AND SEMANTIC ACCURACY RULES:

1. Each action node must be assigned to the partition
   of the actual actor or system component responsible
   for performing that action.

2. Do not assign an action to an external system if
   the action description actually describes an action
   performed by the main system, and vice versa.

3. When the SRS describes interaction with an external
   system, represent the responsibility accurately.
   For example, distinguish between sending a request
   by the main system and processing that request
   by the external system when both actions are relevant.

4. Use neutral and accurate names for final nodes.
   Do not assume that an order is cancelled, rejected,
   or deleted unless this behavior is explicitly
   supported by the SRS.

5. Do not introduce business outcomes or state changes
   that are not explicitly supported by the SRS.

6. Ensure that node names, descriptions, partitions,
   and flow conditions are consistent with each other.

7. When an activity involves an actor making a choice
   followed by the system performing an operation,
   represent these as separate actions when both
   responsibilities are described in the SRS.

8. Do not assign system operations to users merely
   because they initiate or request them.

9. Represent user decisions explicitly when the SRS
   states that an action depends on the user's choice.

OUTPUT REQUIREMENTS:

Return only valid JSON matching the provided response schema.

Use camelCase property names:
- diagramType
- systemName
- activityName
- nodes
- flows
- nodeType
- partition
- source
- target
- condition


WORKFLOW AND LOOP VALIDATION RULES:

1. Do not create retry loops, repeated actions, or
   alternative recovery workflows unless the SRS
   explicitly describes them.

2. Do not assume that users can retry, modify, or
   restart an operation after failure unless this
   behavior is specified in the SRS.

3. Every decision branch must represent an outcome
   supported by the SRS. Do not invent actions or
   transitions to handle unspecified outcomes.

4. When an operation fails, represent only the
   failure handling behavior explicitly described
   in the SRS. Do not automatically retry the
   operation or return to a previous action.

5. If an action is included in the workflow and
   has multiple possible outcomes described in
   the SRS, represent those outcomes accurately.

6. Do not include an action in the workflow unless
   its position and relationship with the other
   actions are supported by the SRS.


The diagramType must be "activity".

Do not include Markdown, explanations, comments, or text
outside the JSON response.
"""




def generate_activity_diagram(
    srs_content: str,
) -> ActivityDiagramResult:

    if not srs_content.strip():
        raise ValueError("SRS content cannot be empty")

    schema = clean_schema(
        ActivityDiagramResult.model_json_schema(by_alias=True)
    )

    # Step 1: Generate the initial activity diagram
    prompt = ACTIVITY_DIAGRAM_PROMPT.format(
        srs_content=srs_content
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.2,
            max_output_tokens=5000,
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty activity diagram"
        )
    
    initial_result = ActivityDiagramResult.model_validate_json(
        response.text
    )

    # Step 2: Review and correct the generated diagram
    diagram_content = json.dumps(
        initial_result.model_dump(by_alias=True),
        ensure_ascii=False,
        indent=2,
    )

    review_prompt = ACTIVITY_DIAGRAM_REVIEW_PROMPT.format(
        srs_content=srs_content,
        diagram_content=diagram_content,
    )

    review_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=review_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
            max_output_tokens=5000,
        ),
    )

    if not review_response.text:
        raise ValueError(
            "Gemini returned an empty reviewed activity diagram"
        )

    # Step 3: Validate the reviewed diagram
    return ActivityDiagramResult.model_validate_json(
        review_response.text
    )


ACTIVITY_DIAGRAM_REVIEW_PROMPT = """
You are a Senior Software Engineer specialized in
UML Activity Diagram validation.

Your task is to review and correct an AI-generated
Activity Diagram by comparing it against the original SRS.

SRS:
{srs_content}

GENERATED ACTIVITY DIAGRAM:
{diagram_content}

VALIDATION RULES:

1. Verify that every activity and transition is supported
   by the SRS.

2. Verify that actor actions and system operations are
   assigned to the correct partitions.

3. When the SRS describes a user choice that determines
   whether an operation is performed, ensure that this
   choice is represented by a decision node.

4. Do not represent an optional user action as an
   automatic system operation.

5. Distinguish between an actor requesting an operation
   and the system executing that operation.

6. Verify that all required conditions and validations
   are represented in the correct order.

7. Verify that decision branches represent all relevant
   outcomes explicitly supported by the SRS.

8. Do not invent missing actions, decisions, business
   rules, recovery behavior, or transitions.

9. Do not add independent workflows that are unrelated
   to the selected workflow.

10. Preserve the original workflow scope when it is
    consistent with the SRS.

11. Correct only issues that can be justified by the SRS.

12. Preserve valid nodes and flows. Do not unnecessarily
    restructure a correct diagram.

13. Ensure that all node IDs are unique and all flow
    references point to existing nodes.

14. Ensure that the corrected diagram satisfies the
    Activity Diagram response schema.


15. OPTIONAL USER ACTIONS:

When the SRS states that a user may choose
whether to perform an action, the diagram must
represent that choice explicitly using a decision node.

The decision must have separate Yes and No branches.

The system operation must only happen on the
branch where the user agrees to perform the action.

Do not connect a negative system validation result
directly to an optional action without representing
the user's choice first.

16. EXTERNAL SERVICES AND PARTITIONS:

When the system sends a request or notification
through an external service, assign the sending
action to the System partition.

Do not assign system-initiated operations to
the external service partition.

Use an external service partition only when the
service itself performs an explicitly described
activity.

17. INITIAL NODE:

The initial node must have a null partition.


OUTPUT REQUIREMENTS:

Return only the corrected diagram as valid JSON.

Use the same response schema and camelCase property names.

Do not include explanations, comments, Markdown,
or text outside the JSON response.

If the original diagram is already correct,
return it without unnecessary changes.

If the SRS states that the user can choose to join
a waiting list, the corrected diagram must contain:

1. A decision node representing the student's choice.
2. A Yes branch leading to a System action that adds
   the student to the waiting list.
3. A No branch leading to the workflow end.

A description saying "when requested" is not a
substitute for explicitly representing the decision
and its two outgoing flows.

18. SEPARATE ACTIVITIES AND EXTERNAL SYSTEM INTERACTIONS:

When the SRS describes multiple distinct activities
performed sequentially, represent them as separate
action nodes instead of combining them into one node.

When an external system performs an operation and
returns a result, represent the external system's
operation as a separate action node using its own
partition.

The system's request and the external system's
processing must not be represented as the same action.

When the system performs two distinct operations,
such as confirming an order and sending a notification,
represent them as separate action nodes if both are
explicitly described in the SRS.

Preserve the correct execution order and do not invent
additional activities.


19. PARALLEL ACTIVITIES:

Analyze activities that occur after the same preceding
activity to determine whether they are sequential or
independent.

If the SRS describes two or more independent activities
that occur after the same preceding activity, and does
not establish a dependency or execution order between
them, represent them as parallel activities.

In this case:
- Add one fork node after the preceding activity.
- Connect the fork node to each independent activity.
- Add a join node after the parallel activities if all
  branches must complete before the workflow ends
  or continues.
- Connect each parallel activity to the join node.
- Connect the join node to the next activity or final node.

Do not connect independent activities sequentially
unless the SRS explicitly establishes that order.

Do not assume activities are parallel if the SRS
establishes a dependency between them.

Do not invent parallel activities that are not supported
by the SRS.


"""



OBJECT_DIAGRAM_PROMPT = """
You are a Senior Software Engineer specialized in UML Object Diagrams.

Your task is to generate a meaningful and accurate UML Object Diagram
based strictly on the latest approved Software Requirements
Specification (SRS).

LATEST APPROVED SRS:
{srs_content}

========================================
1. UNDERSTAND THE SYSTEM
========================================

1. Analyze the complete SRS before generating the diagram.
2. Identify the system's main actors, domain entities,
   business concepts, and external systems.
3. Review all functional requirements to understand
   the system's main workflow.
4. Identify the important entities and relationships
   involved in that workflow.

========================================
2. SELECT A COHERENT SYSTEM SNAPSHOT
========================================

1. An Object Diagram represents a specific snapshot
   of the system at a particular point in time.

2. Select one meaningful scenario that represents
   an important part of the system's core functionality.

3. Choose a consistent system state for that scenario.
   Do not combine incompatible states from different
   stages of the workflow.

4. Select the objects needed to represent that scenario.

5. Include the main actors and domain entities involved
   in the selected scenario when they contribute
   to understanding the system.

6. Ensure that the selected objects collectively
   represent the important parts of the chosen scenario.

7. Do not generate an object for every entity or concept
   mentioned in the SRS.

8. Do not omit essential objects that are necessary
   to understand the selected workflow.

9. Avoid unnecessary, irrelevant, or redundant objects.

========================================
3. OBJECT IDENTIFICATION
========================================

1. Every object must represent a specific instance
   of a class or relevant domain entity.

2. Do not generate class definitions or Class Diagrams.

3. Use meaningful instance names, such as customer1,
   book1, or order1.

4. The className must identify the type of the instance,
   such as Customer, Book, or Order.

5. Actors may be represented as object instances
   when they participate in the selected scenario.

6. Do not confuse an external service with a domain entity.
   External services must not be represented as internal
   business objects unless the SRS explicitly describes
   them as relevant object instances.

7. Do not represent actions, processes, or functional
   requirements as objects.

========================================
4. ATTRIBUTE EXTRACTION
========================================

1. Identify meaningful attributes for each selected object
   based on the SRS.

2. Distinguish between attribute definitions and actual
   attribute values.

   The SRS may describe which attributes an entity has
   without providing their actual values.

   In such cases:
   - Include the attribute only if the schema and diagram
     design require it and its value can be established.
   - Never generate example values, realistic sample data,
     or values based on general knowledge.
   - Do not use real book titles, author names, prices,
     customer names, or other illustrative data unless
     explicitly provided in the SRS.

3. You may derive a state value when it follows directly
   from an explicitly described requirement and the
   selected snapshot.

4. For example, if the selected snapshot represents
   an appointment after successful confirmation,
   its status may be "Confirmed".

5. Do not invent personal information, names, dates,
   prices, specialties, quantities, or arbitrary values.

6. Do not use placeholder values such as:
   "Book Title", "Book Author", "Sample Value",
   "Unknown", or "Not Specified".

7. Do not treat an available option as an actual
   selected value.

8. Do not include attributes whose values cannot
   be established.

9. Empty attribute lists are acceptable when the SRS
   does not provide enough information.

10. Prefer meaningful and supported attributes over
    filling objects with invented data.

ATTRIBUTE VALUE RULE:

Do not generate sample object data.

For each attribute:
- Include a value only if the exact value appears in the SRS.
- A value may be inferred only when it represents a state
  explicitly established by the selected scenario.
- Never generate example IDs, codes, names, numbers,
  prices, or other realistic-looking values.
- If the SRS provides only the attribute name, omit it.


STRICT VALUE TRACEABILITY:

Every attribute value must be traceable to an explicit
statement in the SRS or a state directly established
by the selected scenario.

The existence of an attribute does not authorize
generating its value.

Before including any attribute value, verify its source
in the SRS.

If no supporting source exists, omit the attribute.

Never use domain knowledge, common examples, assumptions,
or realistic sample data to fill missing values.

========================================
5. RELATIONSHIP IDENTIFICATION
========================================

1. Identify relationships between the selected object
   instances based on the SRS.

2. Every link must represent a meaningful relationship
   between its source and target objects.

3. Derive links from explicit associations or relationships
   described by the functional requirements.

4. Use concise relationship labels such as:
   owns, contains, places, belongsTo, or assignedTo,
   when appropriate.

5. Do not represent an interaction with an external
   service as an internal object relationship.

6. Do not create links merely because two concepts
   appear in the same functional requirement.

7. Do not create unsupported, duplicate, or unnecessary links.

8. Every link source and target must reference an existing
   object ID.

========================================
6. OBJECT DIAGRAM QUALITY
========================================

Before generating the output, verify that:

1. The diagram represents one coherent system snapshot.
2. The selected objects represent the main scenario.
3. Every object is a valid instance, not a class definition.
4. Object names and class names are meaningful.
5. Attributes contain supported values only.
6. Placeholder and invented values are absent.
7. Links represent valid relationships between instances.
8. External services are not confused with domain objects.
9. The diagram is neither unnecessarily small nor unnecessarily
   complex.
10. The diagram accurately reflects the SRS.

========================================
7. OUTPUT REQUIREMENTS
========================================

- Use the exact system name specified in the SRS.
- The diagramType must be "object".
- Every object must have a unique diagram-local ID.
- Every object must have a name and className.
- Every attribute must have a name and a non-empty value.
- Attribute names must not be duplicated within an object.
- Every link must have a source, target, and label.
- All link references must point to existing object IDs.
- Follow the provided JSON response schema.
- Use camelCase property names.

Return only valid JSON matching the provided schema.
Do not include Markdown, explanations, comments,
or text outside the JSON.
"""


OBJECT_DIAGRAM_REVIEW_PROMPT = """
You are a Senior Software Engineer specialized in UML
Object Diagram validation.

Your task is to review the generated Object Diagram
against the latest approved SRS.

LATEST APPROVED SRS:
{srs_content}

GENERATED OBJECT DIAGRAM:
{diagram_content}

========================================
1. SNAPSHOT VALIDATION
========================================

1. Verify that the diagram represents one coherent
   system snapshot.

2. Verify that the objects belong to the same meaningful
   scenario and do not combine incompatible system states.

3. Verify that the diagram represents important parts
   of the selected workflow.

========================================
2. OBJECT VALIDATION
========================================

1. Verify that every object represents an instance,
   not a class definition, action, or process.

2. Verify that each object has a meaningful name
   and className.

3. Verify that actors and domain entities are represented
   appropriately.

4. Verify that external services are not incorrectly
   represented as internal domain objects.

5. Preserve relevant objects that are supported by
   the SRS and contribute to the selected scenario.

6. Add a missing essential object only when its relevance
   is clearly supported by the SRS.

7. Remove objects only when they are irrelevant,
   duplicated, or unsupported.

========================================
3. ATTRIBUTE VALIDATION
========================================

1. Verify that attribute names are meaningful.

2. Verify that attribute values are supported by the SRS
   or directly established by the selected snapshot.

3. Remove invented, arbitrary, or placeholder values.

4. Preserve valid derived state values when they follow
   directly from the selected scenario.

5. Do not remove an otherwise valid object merely because
   its attributes list is empty.

6. Do not invent attribute values to make the diagram
   appear more complete.

========================================
4. LINK VALIDATION
========================================

1. Verify that every link represents a meaningful
   relationship between object instances.

2. Verify that source and target IDs exist.

3. Remove unsupported, duplicate, or invalid links.

4. Add a missing link only when the relationship
   is clearly supported by the SRS.

5. Use concise and meaningful relationship labels.

6. Do not represent external service interactions
   as internal object relationships.

========================================
5. FINAL VALIDATION
========================================

Verify that:

- Object IDs are unique.
- Object names are unique.
- Every object has a valid className.
- Attribute names are unique within each object.
- Attribute values are non-empty and supported.
- Every link references existing objects.
- No placeholder values remain.
- The diagram follows the response schema.
- The diagram remains a UML Object Diagram.

Preserve all correct parts of the original diagram.
Do not unnecessarily restructure or simplify it.
Do not add unsupported information.

OUTPUT REQUIREMENTS:

- Preserve the JSON structure.
- Use camelCase property names.
- The diagramType must be "object".
- Return only valid JSON.
- Do not include explanations, comments, or Markdown.

If the original diagram is already correct,
return it without unnecessary changes.
"""


def generate_object_diagram(
    srs_content: str,
) -> ObjectDiagramResult:

    if not srs_content.strip():
        raise ValueError("SRS content cannot be empty")

    schema = clean_schema(
        ObjectDiagramResult.model_json_schema(by_alias=True)
    )

    # Step 1: Generate the initial object diagram
    prompt = OBJECT_DIAGRAM_PROMPT.format(
        srs_content=srs_content
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.2,
            max_output_tokens=5000,
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty object diagram"
        )

    initial_result = ObjectDiagramResult.model_validate_json(
        response.text
    )

    # Step 2: Review and correct the generated diagram
    diagram_content = json.dumps(
        initial_result.model_dump(by_alias=True),
        ensure_ascii=False,
        indent=2,
    )

    review_prompt = OBJECT_DIAGRAM_REVIEW_PROMPT.format(
        srs_content=srs_content,
        diagram_content=diagram_content,
    )

    review_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=review_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
            max_output_tokens=5000,
        ),
    )

    if not review_response.text:
        raise ValueError(
            "Gemini returned an empty reviewed object diagram"
        )

    return ObjectDiagramResult.model_validate_json(
        review_response.text
    )
