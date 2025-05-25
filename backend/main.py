from fastapi import FastAPI, UploadFile, File
from .services.ocr_parser import parse_statement
from .services.categorizer import classify_transactions

app = FastAPI()

@app.post("/upload/")
async def upload_statement(file: UploadFile = File(...)):
    transactions = parse_statement(await file.read())
    categorized = classify_transactions(transactions)
    return {"categorized": categorized}
