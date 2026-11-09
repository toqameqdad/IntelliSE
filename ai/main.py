import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from schemas import (
    ClarificationAnswersInput,
    ClarificationResult,
    ProjectInput,
    RequirementsGenerationInput,
    RequirementsResult,
)
from gemini_service import (
    analyze_project,
    generate_requirements,
    reanalyze_project,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IntelliSE AI Service",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post(
    "/api/ai/requirements/clarify",
    response_model=ClarificationResult,
)
def clarify_project(project: ProjectInput):
    try:
        return analyze_project(project)

    except Exception:
        logger.exception("Project clarification failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to analyze project description.",
            },
        )


@app.post(
    "/api/ai/requirements/clarify/answer",
    response_model=ClarificationResult,
)
def process_clarification_answers(
    data: ClarificationAnswersInput,
):
    try:
        return reanalyze_project(data)

    except Exception:
        logger.exception("Clarification answer processing failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to reanalyze project information.",
            },
        )


@app.post(
    "/api/ai/requirements/generate",
    response_model=RequirementsResult,
)
def generate_project_requirements(
    project: RequirementsGenerationInput,
):
    try:
        return generate_requirements(project)

    except Exception:
        logger.exception("Requirements generation failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to generate requirements.",
            },
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "code": "INVALID_INPUT",
            "message": "Invalid project input.",
        },
    )
