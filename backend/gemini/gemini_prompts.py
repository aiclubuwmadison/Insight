def build_prompt(code: str, language: str) -> str:
    lang_hint = f"The code is written in {language}." if language != "unknown" else ""

    return f"""You are a concise code explainer. A user has just pasted the following code into their editor.

{lang_hint}

Your job:
1. Briefly explain what this code does in plain English.
2. Summarize the key logic steps (2–4 bullet points max).
3. If the code is incomplete or partial, still do your best — note that it appears incomplete.
4. Keep your response under 150 words total.
5. Do NOT include markdown formatting, code fences, or headers in your response.

Code:
{code}

Explanation:"""