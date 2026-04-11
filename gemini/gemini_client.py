from google import genai
from core.config import GEMINI_API_KEY, GEMINI_MODEL
from gemini.prompts import build_prompt

client = genai.Client(api_key=GEMINI_API_KEY)


def get_gemini_explanation(code: str, language: str, source: str) -> str:
    prompt = build_prompt(code=code, language=language)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
    except Exception as e:
        raise RuntimeError(f"Gemini request failed: {e}")

    if not response or not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return _clean_response(response.text)


def _clean_response(raw: str) -> str:
    import re
    cleaned = re.sub(r"```[\w]*\n?", "", raw)
    cleaned = re.sub(r"```", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()