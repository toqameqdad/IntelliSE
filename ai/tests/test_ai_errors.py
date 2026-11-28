"""Verify safe HTTP responses for upstream AI errors."""

import json

import pytest

from ai_errors import generation_error_response


class UpstreamError(Exception):
    def __init__(self, code):
        super().__init__("sensitive upstream diagnostic")
        self.code = code


@pytest.mark.parametrize(
    "error, expected_status, expected_code",
    [
        (UpstreamError(429), 429, "AI_RATE_LIMITED"),
        (UpstreamError("RESOURCE_EXHAUSTED"), 429, "AI_RATE_LIMITED"),
        (TimeoutError("sensitive timeout"), 504, "AI_TIMEOUT"),
        (UpstreamError(504), 504, "AI_TIMEOUT"),
        (UpstreamError("DEADLINE_EXCEEDED"), 504, "AI_TIMEOUT"),
        (UpstreamError(503), 503, "AI_UNAVAILABLE"),
        (UpstreamError("UNAVAILABLE"), 503, "AI_UNAVAILABLE"),
        (ValueError("sensitive internal error"), 500, "AI_GENERATION_FAILED"),
    ],
)
def test_error_response_classification(error, expected_status, expected_code):
    response = generation_error_response(error, "Failed to generate SRS.")
    payload = json.loads(response.body)
    assert response.status_code == expected_status
    assert payload["code"] == expected_code
    assert "sensitive" not in str(payload)


def test_unknown_error_preserves_safe_endpoint_message():
    response = generation_error_response(RuntimeError("secret"), "Failed to generate SRS.")
    assert json.loads(response.body)["message"] == "Failed to generate SRS."
