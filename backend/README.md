# Insight Backend

Insight is a VS Code extension backend that analyzes pasted or selected code. It uses a fast local Tree-sitter + scikit-learn pipeline for common algorithmic patterns and falls back to Gemini when the local model cannot classify code confidently.

## Architecture

1. The VS Code extension sends code, language, and source metadata to `/analyze`.
2. The backend normalizes the request.
3. The local path attempts to parse the code with Tree-sitter.
4. AST features are extracted, including node counts, nesting depth, loop counts, function patterns, and collection usage.
5. A scikit-learn classifier predicts the likely algorithmic pattern.
6. If confidence is at least `0.75`, the backend returns a local explanation and skips Gemini.
7. If parsing fails or confidence is too low, the backend calls Gemini for a general explanation.

## Key files

```text
backend/app/core/language_config.py   # 50+ language aliases and grammar mapping
backend/app/core/parser.py            # Tree-sitter parser setup
backend/app/core/ast_features.py      # AST feature extraction
backend/app/models/train_model.py     # Training script for algorithm classifier
backend/app/models/predict.py         # Model loading and inference
backend/app/models/algorithm_classifier.pkl # Generated classifier model
backend/app/services/analyze.py       # Local model first, Gemini fallback
```

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
```

Create a `.env` file with:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
```

## Train the local classifier

From the backend root or repo root, run:

```bash
python -m app.models.train_model
```

This generates:

```text
backend/app/models/algorithm_classifier.pkl
```

## Run the API

```bash
uvicorn app.main:app --reload
```

## Analyze endpoint

`POST /analyze`

Example request:

```json
{
  "code": "def search(nums, target):\n    l, r = 0, len(nums)-1\n    while l <= r:\n        mid = (l+r)//2\n        if nums[mid] == target: return mid\n        if nums[mid] < target: l = mid + 1\n        else: r = mid - 1\n    return -1",
  "language": "python",
  "source": "paste"
}
```

Example local-model response:

```json
{
  "explanation": "This code appears to use binary search, repeatedly cutting a sorted search range in half until it finds the target or exhausts the range.",
  "time_complexity": "O(log n)",
  "space_complexity": "O(1)",
  "model": "local_algorithm_classifier",
  "algorithm": "binary_search",
  "confidence": 0.91,
  "gemini_used": false,
  "analysis_source": "local_model",
  "status": "success"
}
```

## Why this supports the latency optimization claim

The Gemini call is skipped only when the local classifier returns a known algorithm label above the confidence threshold. This makes the optimization traceable in code through the `gemini_used` and `analysis_source` response fields.

Do not claim a specific latency reduction percentage until you add benchmark logs comparing local-model response time against Gemini response time.
