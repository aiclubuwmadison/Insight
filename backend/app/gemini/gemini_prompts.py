def build_prompt(code: str, language: str) -> str:
    lang_hint = f"The code is written in {language}." if language != "unknown" else ""

    return f"""You are a concise code explainer. A user has pasted code into their editor.

{lang_hint}

Respond in exactly this plain-text format:

Explanation:
<1-2 sentence explanation>

Key Steps:
- step 1
- step 2
- step 3 (if needed)

Time Complexity:
<big-O estimate or Unknown>

Space Complexity:
<big-O estimate or Unknown>

Rules:
- Max 180 words total
- Use plain text only
- No markdown code fences
- If the code is incomplete, say so briefly
- If complexity cannot be determined confidently, say Unknown

Code:
{code}

Response:"""