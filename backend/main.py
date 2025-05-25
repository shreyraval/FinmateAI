from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .services.ocr_parser import parse_statement
from .services.categorizer import classify_transactions
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinMate API",
    description="API for parsing and categorizing bank statements",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/", response_model=Dict[str, Any])
async def upload_statement(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a bank statement file.
    
    Args:
        file (UploadFile): The uploaded bank statement file (PDF, CSV, or XLSX)
        
    Returns:
        Dict[str, Any]: Processed and categorized transactions
        
    Raises:
        HTTPException: If file processing fails
    """
    try:
        # Validate file size (e.g., max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:  # 10MB in bytes
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
            
        # Read file content
        file_content = await file.read()
        
        # Parse the statement
        transactions = parse_statement(file_content, file.filename)
        
        # Categorize transactions
        categorized = classify_transactions(transactions)
        
        return {
            "status": "success",
            "message": "File processed successfully",
            "categorized": categorized
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        await file.close()

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )