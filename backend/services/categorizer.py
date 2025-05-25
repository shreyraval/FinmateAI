import pandas as pd
from typing import Dict, List, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define transaction categories
CATEGORIES = {
    "FOOD": ["whole foods", "trader joe's", "safeway", "restaurant", "cafe", "coffee"],
    "ENTERTAINMENT": ["netflix", "spotify", "hulu", "amazon prime", "movie", "theater"],
    "TRANSPORTATION": ["uber", "lyft", "taxi", "gas", "fuel", "parking"],
    "SHOPPING": ["amazon", "target", "walmart", "costco"],
    "UTILITIES": ["electricity", "water", "gas", "internet", "phone"],
    "HOUSING": ["rent", "mortgage", "property tax", "home insurance"],
    "HEALTHCARE": ["pharmacy", "doctor", "hospital", "medical"],
    "INCOME": ["salary", "deposit", "transfer in"],
    "OTHER": []  # Default category
}

def classify_transactions(transactions: pd.DataFrame) -> Dict[str, Any]:
    """
    Categorize transactions based on their descriptions.
    
    Args:
        transactions (pd.DataFrame): DataFrame containing transaction data
            Expected columns: 'Date', 'Description', 'Amount'
            
    Returns:
        Dict[str, Any]: Dictionary containing categorized transactions and summary
        
    Raises:
        ValueError: If required columns are missing
        Exception: For other processing errors
    """
    try:
        # Validate required columns
        required_columns = ['Date', 'Description', 'Amount']
        missing_columns = [col for col in required_columns if col not in transactions.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
        # Convert description to lowercase for case-insensitive matching
        transactions['Description'] = transactions['Description'].str.lower()
        
        # Initialize categories
        categorized_transactions = {category: [] for category in CATEGORIES.keys()}
        
        # Categorize each transaction
        for _, row in transactions.iterrows():
            description = row['Description']
            category_found = False
            
            # Try to match transaction with categories
            for category, keywords in CATEGORIES.items():
                if any(keyword in description for keyword in keywords):
                    categorized_transactions[category].append({
                        'date': row['Date'],
                        'description': description,
                        'amount': float(row['Amount'])
                    })
                    category_found = True
                    break
            
            # If no category found, add to OTHER
            if not category_found:
                categorized_transactions['OTHER'].append({
                    'date': row['Date'],
                    'description': description,
                    'amount': float(row['Amount'])
                })
        
        # Calculate summary statistics
        summary = _calculate_summary(categorized_transactions)
        
        return {
            'transactions': categorized_transactions,
            'summary': summary
        }
        
    except Exception as e:
        logger.error(f"Error categorizing transactions: {str(e)}")
        raise Exception(f"Error categorizing transactions: {str(e)}")

def _calculate_summary(categorized_transactions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
    """
    Calculate summary statistics for each category.
    
    Args:
        categorized_transactions (Dict[str, List[Dict[str, Any]]]): Categorized transactions
        
    Returns:
        Dict[str, float]: Summary statistics for each category
    """
    summary = {}
    
    for category, transactions in categorized_transactions.items():
        if transactions:
            total_amount = sum(t['amount'] for t in transactions)
            transaction_count = len(transactions)
            summary[category] = {
                'total_amount': round(total_amount, 2),
                'transaction_count': transaction_count,
                'average_amount': round(total_amount / transaction_count, 2) if transaction_count > 0 else 0
            }
        else:
            summary[category] = {
                'total_amount': 0,
                'transaction_count': 0,
                'average_amount': 0
            }
    
    return summary