from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from services.ocr_parser import parse_statement
from services.categorizer import classify_transactions
from agents.advisor_agent import generate_budget_advice
from agents.qa_agent import answer_question
from services.plaid_service import plaid_service
from database import get_db, engine
from models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(title="FinmateAI API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3001")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str
    user_id: int

class GoogleAuthRequest(BaseModel):
    code: str

class PlaidLinkTokenRequest(BaseModel):
    user_id: str

class PlaidCallbackRequest(BaseModel):
    public_token: str

class PlaidSyncRequest(BaseModel):
    access_token: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/auth/google")
async def google_auth(request: GoogleAuthRequest):
    # TODO: Implement OAuth2 code exchange
    return {"message": "OAuth2 authentication placeholder"}

@app.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        contents = await file.read()
        df = parse_statement(contents, file.filename)
        categorized = classify_transactions(df)
        # TODO: Store transactions in database using async db
        # Example: await db.execute(...)
        return {
            "message": "Statement processed successfully",
            "transactions": categorized.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
async def analyze_transactions(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        contents = await file.read()
        df = parse_statement(contents, file.filename)
        categorized = classify_transactions(df)
        advice = generate_budget_advice(categorized)
        # TODO: Store transactions in database using async db
        return {
            "transactions": categorized.to_dict(orient="records"),
            "advice": advice
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        answer = answer_question(request.question, request.user_id, db)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/plaid/link-token")
async def create_link_token(request: PlaidLinkTokenRequest):
    """
    Create a Plaid link token for initializing Plaid Link.
    """
    try:
        response = await plaid_service.create_link_token(request.user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/plaid/callback")
async def handle_plaid_callback(request: PlaidCallbackRequest):
    """
    Handle the callback from Plaid Link after successful connection.
    """
    try:
        response = await plaid_service.exchange_public_token(request.public_token)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/plaid/sync")
async def sync_transactions(request: PlaidSyncRequest):
    """
    Sync transactions from Plaid for a given date range.
    """
    try:
        transactions = await plaid_service.fetch_transactions(
            request.access_token,
            request.start_date,
            request.end_date
        )
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
