import json
import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

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
    DiagramGenerationInput,
)
from gemini_service import (
    analyze_project,
    generate_requirements,
    reanalyze_project,
    generate_srs,
    generate_context_diagram,
    generate_use_case_diagram,
    generate_activity_diagram,
    generate_object_diagram,
    recommend_methodology,
    analyze_methodology_compatibility,
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


@app.post(
    "/api/ai/srs/generate",
    response_model=SRSResult,
)
def generate_project_srs(data: SRSInput):
    try:
        return generate_srs(data)

    except Exception:
        logger.exception("SRS generation failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to generate SRS.",
            },
        )


@app.post(
    "/api/ai/methodology/recommend",
    response_model=MethodologyRecommendationResult,
)
def recommend_project_methodology(data: MethodologyInput):
    try:
        return recommend_methodology(data)

    except Exception:
        logger.exception("Methodology recommendation failed")
        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to recommend development methodology.",
            },
        )


@app.post(
    "/api/ai/methodology/compatibility",
    response_model=MethodologyCompatibilityResult,
)
def analyze_project_methodology_compatibility(
    data: MethodologyCompatibilityInput,
):
    try:
        return analyze_methodology_compatibility(data)

    except Exception:
        logger.exception("Methodology compatibility analysis failed")
        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to analyze methodology compatibility.",
            },
        )


@app.post(
    "/api/ai/diagrams/context/generate",
    response_model=ContextDiagramResult,
)
def generate_project_context_diagram(data: DiagramGenerationInput):
    try:
        srs_content = json.dumps(data.root, ensure_ascii=False)

        return generate_context_diagram(srs_content)

    except Exception:
        logger.exception("Context diagram generation failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to generate context diagram.",
            },
        )


@app.post(
    "/api/ai/diagrams/use-case/generate",
    response_model=UseCaseDiagramResult,
)
def generate_project_use_case_diagram(data: DiagramGenerationInput):
    try:
        srs_content = json.dumps(data.root, ensure_ascii=False)

        return generate_use_case_diagram(srs_content)

    except Exception:
        logger.exception("Use case diagram generation failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to generate use case diagram.",
            },
        )



@app.post(
    "/api/ai/diagrams/activity/generate",
    response_model=ActivityDiagramResult,
)
@app.post(
    "/generate-activity-diagram",
    response_model=ActivityDiagramResult,
    include_in_schema=False,
)
def generate_activity_diagram_endpoint(data: DiagramGenerationInput):

    try:
        srs_content = json.dumps(
            data.root,
            ensure_ascii=False,
        )

        result = generate_activity_diagram(srs_content)

        return result

    except Exception:
        logger.exception("Activity diagram generation failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to generate activity diagram.",
            },
        )



@app.post(
    "/api/ai/diagrams/object/generate",
    response_model=ObjectDiagramResult,
)
@app.post(
    "/generate-object-diagram",
    response_model=ObjectDiagramResult,
    include_in_schema=False,
)
def generate_object_diagram_endpoint(data: DiagramGenerationInput):

    try:
        srs_content = json.dumps(
            data.root,
            ensure_ascii=False,
        )

        result = generate_object_diagram(srs_content)

        return result

    except Exception:
        logger.exception("Object diagram generation failed")

        return JSONResponse(
            status_code=500,
            content={
                "code": "AI_GENERATION_FAILED",
                "message": "Failed to generate object diagram.",
            },
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "code": "INVALID_INPUT",
            "message": "Invalid project input.",
            "details": jsonable_encoder(exc.errors()),
        },
    )

