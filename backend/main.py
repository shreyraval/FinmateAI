from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import pandas as pd

from services.ocr_parser import parse_statement
from services.categorizer import classify_transactions
from agents.advisor_agent import generate_budget_advice

load_dotenv()

app = FastAPI()

# CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze/")
async def analyze_transactions(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = parse_statement(contents, file.filename)
        categorized = classify_transactions(df)
        advice = generate_budget_advice(categorized)
        return {
            "transactions": categorized.to_dict(orient="records"),
            "advice": advice
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
