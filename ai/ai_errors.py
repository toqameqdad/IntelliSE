"""Translate upstream AI failures into stable, safe API responses."""

from fastapi.responses import JSONResponse


def generation_error_response(exc: Exception, message: str) -> JSONResponse:
    """Use upstream status metadata, never exception text, in client responses."""
    status = getattr(exc, "code", None)
    if status is None:
        status = getattr(exc, "status_code", None)

    if status == 429 or status == "RESOURCE_EXHAUSTED":
        return JSONResponse(
            status_code=429,
            content={
                "code": "AI_RATE_LIMITED",
                "message": "AI service is busy. Please try again later.",
            },
        )

    if status == 504 or status == "DEADLINE_EXCEEDED" or isinstance(exc, TimeoutError):
        return JSONResponse(
            status_code=504,
            content={
                "code": "AI_TIMEOUT",
                "message": "AI service timed out. Please try again.",
            },
        )

    if status in (502, 503, "UNAVAILABLE"):
        return JSONResponse(
            status_code=503,
            content={
                "code": "AI_UNAVAILABLE",
                "message": "AI service is temporarily unavailable.",
            },
        )

    return JSONResponse(
        status_code=500,
        content={"code": "AI_GENERATION_FAILED", "message": message},
    )
