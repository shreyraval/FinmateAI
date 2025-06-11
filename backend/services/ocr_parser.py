import pandas as pd
import pdfplumber
import re
from io import BytesIO
from typing import Union, List, Dict
import logging

logger = logging.getLogger(__name__)

def parse_statement(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """
    Parse bank statement files (CSV, XLSX, PDF) and extract transaction data.
    
    Args:
        file_bytes: Raw bytes of the uploaded file
        filename: Original filename with extension
        
    Returns:
        DataFrame with columns [date, description, amount]
    """
    file_ext = filename.lower().split('.')[-1]
    
    try:
        if file_ext in ['csv', 'xlsx', 'xls']:
            return _parse_structured_file(file_bytes, file_ext)
        elif file_ext == 'pdf':
            return _parse_pdf(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    except Exception as e:
        logger.error(f"Error parsing statement {filename}: {str(e)}")
        raise

def _parse_structured_file(file_bytes: bytes, file_ext: str) -> pd.DataFrame:
    """Parse CSV or Excel files using pandas."""
    file_obj = BytesIO(file_bytes)
    
    if file_ext == 'csv':
        # Try different encodings and separators
        try:
            df = pd.read_csv(file_obj, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_obj, encoding='latin1')
    else:  # xlsx or xls
        df = pd.read_excel(file_obj)
    
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Map common column names to our standard format
    column_mapping = {
        'date': ['date', 'transaction date', 'posting date', 'date posted'],
        'description': ['description', 'transaction description', 'details', 'memo', 'narration'],
        'amount': ['amount', 'transaction amount', 'debit', 'credit', 'balance']
    }
    
    # Find matching columns
    mapped_columns = {}
    for target_col, possible_names in column_mapping.items():
        for col in df.columns:
            if any(name in col for name in possible_names):
                mapped_columns[target_col] = col
                break
    
    # Rename columns to standard format
    df = df.rename(columns={v: k for k, v in mapped_columns.items()})
    
    # Ensure required columns exist
    required_cols = ['date', 'description', 'amount']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Clean and standardize data
    df['date'] = pd.to_datetime(df['date'])
    df['description'] = df['description'].astype(str).str.strip()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    return df[required_cols]

def _parse_pdf(file_bytes: bytes) -> pd.DataFrame:
    """Parse PDF statements using pdfplumber and regex patterns."""
    transactions = []
    
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
                
            # Common patterns for transaction lines
            patterns = [
                # Pattern: Date Description Amount
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s+(.*?)\s+([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})',
                # Pattern: Date Amount Description
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s+([-+]?\$?\d{1,3}(?:,\d{3})*\.\d{2})\s+(.*?)$',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) == 3:
                        date_str, desc, amount = match.groups()
                        # Clean and standardize the data
                        date = pd.to_datetime(date_str)
                        desc = desc.strip()
                        amount = float(amount.replace('$', '').replace(',', ''))
                        
                        transactions.append({
                            'date': date,
                            'description': desc,
                            'amount': amount
                        })
    
    if not transactions:
        raise ValueError("No transactions found in PDF")
    
    return pd.DataFrame(transactions)