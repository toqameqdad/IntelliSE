import unittest

from pydantic import ValidationError

from schemas import Requirement, RequirementsResult


class TestRequirementsValidation(unittest.TestCase):

    def test_valid_requirements(self):
        result = RequirementsResult(
            functional_requirements=[
                Requirement(
                    type="functional",
                    description="Users can create tasks",
                    priority="must",
                    rationale="Task creation is required",
                    source="explicit",
                )
            ],
            non_functional_requirements=[],
        )

        self.assertEqual(len(result.functional_requirements), 1)

    def test_wrong_requirement_type(self):
        with self.assertRaises(ValidationError):
            RequirementsResult(
                functional_requirements=[
                    Requirement(
                        type="non_functional",
                        description="System must be secure",
                        priority="must",
                        rationale="Security is required",
                        source="explicit",
                    )
                ],
                non_functional_requirements=[],
            )

    def test_duplicate_requirements(self):
        requirement = Requirement(
            type="functional",
            description="Users can create tasks",
            priority="must",
            rationale="Task creation is required",
            source="explicit",
        )

        with self.assertRaises(ValidationError):
            RequirementsResult(
                functional_requirements=[
                    requirement,
                    requirement,
                ],
                non_functional_requirements=[],
            )

    def test_empty_description(self):
        with self.assertRaises(ValidationError):
            Requirement(
                type="functional",
                description="",
                priority="must",
                rationale="Task creation is required",
                source="explicit",
            )


    def test_empty_rationale(self):
        with self.assertRaises(ValidationError):
            Requirement(
                type="functional",
                description="Users can create tasks",
                priority="must",
                rationale="",
                source="explicit",
            )


if __name__ == "__main__":
    unittest.main()