from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from services.analyze import run_analysis

app = FastAPI(title="Code Paste Analyzer")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": str(exc.errors()), "status": "error"}
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        explanation = await run_analysis(
            code=request.code,
            language=request.language,
            source=request.source
        )
        return AnalyzeResponse(explanation=explanation)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e), "status": "error"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "status": "error"})