
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=90000,
        retry_options=types.HttpRetryOptions(
            attempts=1
        )
    )
)

print("Sending request to Gemini...", flush=True)
start = time.time()

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with exactly: Hello IntelliSE",
        config=types.GenerateContentConfig(
            max_output_tokens=100
        )
    )

    print("Response:", response.text)

except errors.APIError as e:
    print("API Error:", e.code, e.message)

except Exception as e:
    print("Error:", type(e).__name__, str(e))

finally:
    print(f"Time: {time.time() - start:.2f} seconds")
    client.close()

