import unittest

from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app


client = TestClient(app)


class TestAPI(unittest.TestCase):
    def test_health_check(self):
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_generate_requirements_invalid_input(self):
        response = client.post(
            "/api/ai/requirements/generate",
            json={
                "projectName": "",
                "projectDescription": "Short",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["code"],
            "INVALID_INPUT",
        )
    
    @patch("main.generate_requirements")
    def test_generate_requirements_success(self, mock_generate):
        mock_generate.return_value = {
            "functional_requirements": [],
            "non_functional_requirements": [],
        }

        response = client.post(
            "/api/ai/requirements/generate",
            json={
                "projectName": "Task Manager",
                "projectDescription": (
                    "A web application for managing personal tasks."
                ),
                "answers": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("functionalRequirements", response.json())
        self.assertIn("nonFunctionalRequirements", response.json())
        mock_generate.assert_called_once()

    @patch("main.generate_requirements")
    def test_generate_requirements_ai_failure(self, mock_generate):
        mock_generate.side_effect = Exception("Gemini API error")

        response = client.post(
            "/api/ai/requirements/generate",
            json={
                "projectName": "Task Manager",
                "projectDescription": (
                    "A web application for managing personal tasks."
                ),
                "answers": [],
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["code"],
            "AI_GENERATION_FAILED",
        )

    @patch("main.analyze_project")
    def test_clarify_project_success(self, mock_analyze):
        mock_analyze.return_value = {
            "needs_clarification": True,
            "questions": [
                {
                    "question": "Who can create tasks?",
                    "reason": "The allowed user roles are unclear.",
                    "related_area": "users",
                }
            ],
        }

        response = client.post(
            "/api/ai/requirements/clarify",
            json={
                "projectName": "Task Manager",
                "projectDescription": (
                    "A web application for managing personal tasks."
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["needsClarification"])
        self.assertEqual(len(response.json()["questions"]), 1)
        mock_analyze.assert_called_once() 

    @patch("main.reanalyze_project")
    def test_process_clarification_answers_success(self, mock_reanalyze):
        mock_reanalyze.return_value = {
            "needs_clarification": False,
            "questions": [],
        }

        response = client.post(
            "/api/ai/requirements/clarify/answer",
            json={
                "projectName": "Task Manager",
                "projectDescription": (
                    "A web application for managing personal tasks."
                ),
                "answers": [
                    {
                        "question": "Who can create tasks?",
                        "answer": "Registered users only.",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["needsClarification"])
        self.assertEqual(response.json()["questions"], [])
        mock_reanalyze.assert_called_once()  

    @patch("main.reanalyze_project")
    def test_process_clarification_answers_ai_failure(self, mock_reanalyze):
        mock_reanalyze.side_effect = Exception("Gemini API error")

        response = client.post(
            "/api/ai/requirements/clarify/answer",
            json={
                "projectName": "Task Manager",
                "projectDescription": (
                    "A web application for managing personal tasks."
                ),
                "answers": [
                    {
                        "question": "Who can create tasks?",
                        "answer": "Registered users only.",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["code"],
            "AI_GENERATION_FAILED",
        )
        
if __name__ == "__main__":
    unittest.main()