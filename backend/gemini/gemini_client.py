from google import genai
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.gemini.gemini_prompts import build_prompt
import re


client = genai.Client(api_key=GEMINI_API_KEY)


def get_gemini_explanation(code: str, language: str, source: str) -> str:
    """
    Generate an explanation for the given code using Gemini.
    """
    if not code or not code.strip():
        raise RuntimeError("Invalid request: code is empty")

    if not language or not language.strip():
        raise RuntimeError("Invalid request: language is empty")

    prompt = build_prompt(code=code, language=language)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
    except Exception as e:
        raise RuntimeError(f"Gemini request failed: {e}")

    if not response or not getattr(response, "text", None):
        raise RuntimeError("Gemini returned an empty response")

    cleaned = clean_response(response.text)

    if not cleaned:
        raise RuntimeError("Gemini returned no usable explanation")

    return cleaned


def clean_response(raw: str) -> str:
    """
    Clean Gemini output while preserving the actual explanation text.
    """
    if not raw or not isinstance(raw, str):
        raise ValueError("Gemini returned empty or invalid text")

    cleaned = raw

    # Remove code fence markers but keep enclosed text
    cleaned = re.sub(r"```[\w+-]*\n?", "", cleaned)
    cleaned = re.sub(r"```", "", cleaned)

    # Remove inline backticks
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)

    # Collapse excessive blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Trim trailing spaces on each line
    cleaned = re.sub(r"[ \t]+$", "", cleaned, flags=re.MULTILINE)

    return cleaned.strip()