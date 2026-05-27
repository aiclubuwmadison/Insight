from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from app.services.analyze import run_analysis

app = FastAPI(title="Code Paste Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "running"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    clean_errors = []

    for error in exc.errors():
        clean_error = error.copy()

        if "ctx" in clean_error:
            clean_error["ctx"] = {
                key: str(value)
                for key, value in clean_error["ctx"].items()
            }

        clean_errors.append(clean_error)

    return JSONResponse(
        status_code=422,
        content={"detail": clean_errors},
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        result = await run_analysis(
            code=request.code,
            language=request.language,
            source=request.source
        )

        return AnalyzeResponse(
            explanation=result["explanation"],
            time_complexity=result.get("time_complexity"),
            space_complexity=result.get("space_complexity"),
            model=result.get("model", "gemini"),
            algorithm=result.get("algorithm"),
            confidence=result.get("confidence"),
            gemini_used=result.get("gemini_used", True),
            analysis_source=result.get("analysis_source", "gemini"),
            status="success"
        )

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e), "status": "error"}
        )

    except RuntimeError as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "status": "error"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}", "status": "error"}
        )
