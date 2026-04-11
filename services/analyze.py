from gemini.gemini_client import get_gemini_explanation


def normalize_code(code: str, language: str) -> dict:
    """Clean and prepare code for analysis."""
    normalized = code.strip()  # trim leading/trailing whitespace
    # preserve internal indentation — do NOT strip lines individually
    return {
        "code": normalized,
        "language": language or "unknown",
    }


async def run_analysis(code: str, language: str, source: str) -> str:
    """
    Full analysis pipeline:
    1. Normalize/clean code
    2. Call Gemini
    3. Return explanation string
    """
    if not code or not code.strip():
        raise ValueError("Cannot analyze empty code")

    normalized = normalize_code(code, language)

    try:
        explanation = get_gemini_explanation(
            code=normalized["code"],
            language=normalized["language"],
            source=source
        )
    except RuntimeError as e:
        raise RuntimeError(f"Analysis failed: {e}")

    if not explanation:
        raise RuntimeError("Gemini returned an empty explanation")

    return explanation