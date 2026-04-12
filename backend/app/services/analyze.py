from app.gemini.gemini_client import get_gemini_explanation


def normalize_code(code: str, language: str) -> dict:
    normalized = code.strip()
    return {
        "code": normalized,
        "language": language or "unknown",
    }


async def run_analysis(code: str, language: str, source: str) -> dict:
    if not code or not code.strip():
        raise ValueError("Cannot analyze empty code")

    normalized = normalize_code(code, language)

    try:
        result = get_gemini_explanation(
            code=normalized["code"],
            language=normalized["language"],
            source=source,
        )
    except RuntimeError as e:
        raise RuntimeError(f"Analysis failed: {e}")

    if not result or not result.get("explanation", "").strip():
        raise RuntimeError("Gemini returned an empty explanation")

    return result