from app.core.ast_features import extract_ast_features
from app.core.parser import UnsupportedLanguageError, parse_code
from app.gemini.gemini_client import get_gemini_explanation
from app.models.predict import predict_algorithm

LOCAL_MODEL_CONFIDENCE_THRESHOLD = 0.40

LOCAL_ALGORITHM_EXPLANATIONS = {
    "binary_search": {
        "explanation": "This code appears to use binary search, repeatedly cutting a sorted search range in half until it finds the target or exhausts the range.",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
    },
    "two_pointers": {
        "explanation": "This code appears to use the two pointers pattern, moving two indexes through a sequence to find or compare values efficiently.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
    "sliding_window": {
        "explanation": "This code appears to use a sliding window, maintaining a moving range of elements instead of recomputing each window from scratch.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
    "stack": {
        "explanation": "This code appears to use a stack, storing values in last-in, first-out order to track recent state.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
    },
    "dfs": {
        "explanation": "This code appears to use depth-first search, exploring as far as possible along each branch before backtracking.",
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
    },
    "bfs": {
        "explanation": "This code appears to use breadth-first search, visiting nodes level by level with a queue.",
        "time_complexity": "O(V + E)",
        "space_complexity": "O(V)",
    },
    "dynamic_programming": {
        "explanation": "This code appears to use dynamic programming, storing intermediate results so overlapping subproblems are not recomputed.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
    },
    "sorting": {
        "explanation": "This code appears to sort a collection before returning or using the ordered result.",
        "time_complexity": "O(n log n)",
        "space_complexity": "Depends on the sorting implementation",
    },
    "hash_map": {
        "explanation": "This code appears to use a hash map or dictionary for fast key-based lookups.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
    },
}


def normalize_code(code: str, language: str) -> dict:
    normalized = code.strip()
    return {
        "code": normalized,
        "language": language or "unknown",
    }


def _try_local_algorithm_analysis(code: str, language: str) -> dict | None:
    """
    Try the fast local path before Gemini.

    This is the traceable optimization path:
    Tree-sitter parse -> AST features -> scikit-learn classifier -> skip Gemini
    when confidence is high enough.
    """
    try:
        tree = parse_code(code, language)
        features = extract_ast_features(tree.root_node, code)

        print("AST FEATURES:", features)

        prediction = predict_algorithm(
            features,
            threshold=LOCAL_MODEL_CONFIDENCE_THRESHOLD,
        )

        print("LOCAL MODEL PREDICTION:", prediction)
        print("LOCAL CONFIDENCE THRESHOLD:", LOCAL_MODEL_CONFIDENCE_THRESHOLD)

    except UnsupportedLanguageError as exc:
        print("LOCAL MODEL SKIPPED: unsupported language:", exc)
        return None
    except ValueError as exc:
        print("LOCAL MODEL SKIPPED: value error:", exc)
        return None
    except RuntimeError as exc:
        print("LOCAL MODEL SKIPPED: runtime error:", exc)
        return None
    except Exception as exc:
        print("LOCAL MODEL FAILED:", exc)
        return None

    label = prediction.get("label", "unknown")
    confidence = prediction.get("confidence", 0.0)

    if label == "unknown":
        print("LOCAL MODEL SKIPPED: prediction was unknown")
        return None

    if label not in LOCAL_ALGORITHM_EXPLANATIONS:
        print(f"LOCAL MODEL SKIPPED: no local explanation for label '{label}'")
        return None

    if confidence < LOCAL_MODEL_CONFIDENCE_THRESHOLD:
        print(
            f"LOCAL MODEL SKIPPED: confidence {confidence} below threshold "
            f"{LOCAL_MODEL_CONFIDENCE_THRESHOLD}"
        )
        return None

    local_result = LOCAL_ALGORITHM_EXPLANATIONS[label]

    print(f"LOCAL MODEL USED: {label} with confidence {confidence}")

    return {
        **local_result,
        "model": "local_algorithm_classifier",
        "algorithm": label,
        "confidence": confidence,
        "gemini_used": False,
        "analysis_source": "local_model",
    }


async def run_analysis(code: str, language: str, source: str) -> dict:
    if not code or not code.strip():
        raise ValueError("Cannot analyze empty code")

    normalized = normalize_code(code, language)

    local_result = _try_local_algorithm_analysis(
        code=normalized["code"],
        language=normalized["language"],
    )

    if local_result is not None:
        return local_result

    print("FALLING BACK TO GEMINI")

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

    return {
        **result,
        "model": "gemini",
        "algorithm": None,
        "confidence": None,
        "gemini_used": True,
        "analysis_source": "gemini",
    }