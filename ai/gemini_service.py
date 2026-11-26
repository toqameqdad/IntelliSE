import os

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