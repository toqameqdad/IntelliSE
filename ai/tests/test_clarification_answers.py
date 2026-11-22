from schemas import ClarificationAnswersInput


data = {
    "projectName": "Task Manager",
    "projectDescription": (
        "A task management application for organizing daily tasks."
    ),
    "answers": [
        {
            "question": "Can users assign tasks to others?",
            "answer": "No, users can only manage their own tasks."
        }
    ]
}

invalid_data = {
    "projectName": "Task Manager",
    "projectDescription": (
        "A task management application for organizing daily tasks."
    ),
    "answers": []
}

try:
    ClarificationAnswersInput.model_validate(invalid_data)
except Exception as error:
    print("Validation failed as expected:")
    print(error)

	
result = ClarificationAnswersInput.model_validate(data)

print("Validation successful!")
print(result.model_dump(by_alias=True))