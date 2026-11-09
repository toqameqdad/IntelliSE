import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas import (
    ClarificationAnswersInput,
    ClarificationResult,
    ProjectInput,
    RequirementsGenerationInput,
    RequirementsResult,
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