from google import genai
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.gemini.gemini_prompts import build_prompt
import re


client = genai.Client(api_key=GEMINI_API_KEY)


def get_gemini_explanation(code: str, language: str, source: str) -> dict:
    """
    Generate an explanation and complexity estimates for the given code using Gemini.
    """
    if not code or not code.strip():
        raise RuntimeError("Invalid request: code is empty")

    if not language or not language.strip():
        language = "unknown"

    prompt = build_prompt(code=code, language=language)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
    except Exception as e:
        error_message = str(e)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise RuntimeError("Gemini quota exceeded. Check your API plan, billing, or try a different model.")

        raise RuntimeError(f"Gemini request failed: {error_message}")

    if not response or not getattr(response, "text", None):
        raise RuntimeError("Gemini returned an empty response")

    parsed = parse_response(response.text)

    if not parsed["explanation"]:
        raise RuntimeError("Gemini returned no usable explanation")

    return parsed


def parse_response(raw: str) -> dict:
    """
    Parse Gemini output into structured fields.
    """
    if not raw or not isinstance(raw, str):
        raise ValueError("Gemini returned empty or invalid text")

    cleaned = raw.strip()

    cleaned = re.sub(r"```[\w+-]*\n?", "", cleaned)
    cleaned = re.sub(r"```", "", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+$", "", cleaned, flags=re.MULTILINE)

    explanation = cleaned
    time_complexity = "Unknown"
    space_complexity = "Unknown"

    time_match = re.search(
        r"Time Complexity:\s*(.+?)(?:\n|$)",
        cleaned,
        flags=re.IGNORECASE
    )
    if time_match:
        time_complexity = time_match.group(1).strip()

    space_match = re.search(
        r"Space Complexity:\s*(.+?)(?:\n|$)",
        cleaned,
        flags=re.IGNORECASE
    )
    if space_match:
        space_complexity = space_match.group(1).strip()

    explanation = re.sub(r"^\s*Explanation:\s*", "", explanation, flags=re.IGNORECASE)
    explanation = re.sub(r"\n\s*Key Steps:\s*", "\n", explanation, flags=re.IGNORECASE)
    explanation = re.sub(r"\n\s*Time Complexity:\s*.+?(?=\n|$)", "", explanation, flags=re.IGNORECASE)
    explanation = re.sub(r"\n\s*Space Complexity:\s*.+?(?=\n|$)", "", explanation, flags=re.IGNORECASE)
    explanation = explanation.strip()

    return {
        "explanation": explanation,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
    }