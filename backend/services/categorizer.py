import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define category keywords
CATEGORY_KEYWORDS = {
    'Food & Dining': [
        'restaurant', 'cafe', 'coffee', 'starbucks', 'uber eats', 'doordash', 'grubhub',
        'whole foods', 'trader joe', 'grocery', 'supermarket', 'food', 'dining'
    ],
    'Transportation': [
        'uber', 'lyft', 'taxi', 'transit', 'subway', 'bus', 'train', 'metro',
        'gas', 'fuel', 'shell', 'chevron', 'exxon', 'parking', 'toll'
    ],
    'Shopping': [
        'amazon', 'walmart', 'target', 'costco', 'best buy', 'ikea', 'home depot',
        'nordstrom', 'macy', 'retail', 'store', 'shop'
    ],
    'Entertainment': [
        'netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater', 'concert',
        'ticket', 'event', 'amc', 'regal'
    ],
    'Bills & Utilities': [
        'electric', 'water', 'gas', 'utility', 'internet', 'phone', 'mobile',
        'cable', 'tv', 'streaming', 'subscription'
    ],
    'Health & Fitness': [
        'gym', 'fitness', 'doctor', 'medical', 'pharmacy', 'cvs', 'walgreens',
        'health', 'dental', 'vision', 'insurance'
    ],
    'Travel': [
        'hotel', 'airline', 'flight', 'airbnb', 'booking', 'expedia', 'travel',
        'vacation', 'trip', 'resort'
    ],
    'Education': [
        'school', 'university', 'college', 'tuition', 'course', 'book', 'textbook',
        'education', 'learning', 'student'
    ],
    'Personal Care': [
        'salon', 'spa', 'beauty', 'haircut', 'cosmetic', 'makeup', 'skincare',
        'personal care', 'grooming'
    ],
    'Income': [
        'salary', 'payroll', 'deposit', 'income', 'payment received', 'refund',
        'reimbursement', 'transfer in'
    ]
}

def classify_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify transactions using rule-based keywords and ML fallback.
    
    Args:
        df: DataFrame with columns [date, description, amount]
        
    Returns:
        DataFrame with added 'category' column
    """
    if 'description' not in df.columns:
        raise ValueError("DataFrame must contain 'description' column")
    
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Initialize category column
    df['category'] = None
    
    # First pass: Rule-based classification
    df['category'] = df['description'].apply(
        lambda x: _rule_based_classify(x.lower()) if pd.notnull(x) else None
    )
    
    # Second pass: ML classification for unclassified transactions
    unclassified_mask = df['category'].isna()
    if unclassified_mask.any():
        try:
            ml_categories = _ml_classify(df.loc[unclassified_mask, 'description'])
            df.loc[unclassified_mask, 'category'] = ml_categories
        except Exception as e:
            logger.warning(f"ML classification failed: {str(e)}")
            # If ML fails, mark remaining as "Uncategorized"
            df.loc[unclassified_mask, 'category'] = "Uncategorized"
    
    return df

def _rule_based_classify(description: str) -> Optional[str]:
    """Classify transaction using keyword rules."""
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in description.lower() for keyword in keywords):
            return category
    return None

def _ml_classify(descriptions: pd.Series) -> List[str]:
    """Classify transactions using pre-trained KMeans model."""
    model_path = os.path.join('models', 'transaction_classifier.joblib')
    vectorizer_path = os.path.join('models', 'transaction_vectorizer.joblib')
    
    try:
        # Load pre-trained model and vectorizer
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        # Transform descriptions
        X = vectorizer.transform(descriptions)
        
        # Get predictions
        predictions = model.predict(X)
        
        # Map cluster numbers to categories
        cluster_to_category = {
            0: 'Food & Dining',
            1: 'Transportation',
            2: 'Shopping',
            3: 'Entertainment',
            4: 'Bills & Utilities',
            5: 'Health & Fitness',
            6: 'Travel',
            7: 'Education',
            8: 'Personal Care',
            9: 'Income'
        }
        
        return [cluster_to_category[pred] for pred in predictions]
        
    except FileNotFoundError:
        logger.warning("ML model files not found. Training new model...")
        return _train_and_classify(descriptions)
    except Exception as e:
        logger.error(f"Error in ML classification: {str(e)}")
        raise

def _train_and_classify(descriptions: pd.Series) -> List[str]:
    """Train new model and classify transactions."""
    # Initialize vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    # Transform descriptions
    X = vectorizer.fit_transform(descriptions)
    
    # Train KMeans model
    n_clusters = len(CATEGORY_KEYWORDS)
    model = KMeans(n_clusters=n_clusters, random_state=42)
    predictions = model.fit_predict(X)
    
    # Save model and vectorizer
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, os.path.join('models', 'transaction_classifier.joblib'))
    joblib.dump(vectorizer, os.path.join('models', 'transaction_vectorizer.joblib'))
    
    # Map clusters to categories (this is a simple mapping, could be improved)
    cluster_to_category = {
        i: category for i, category in enumerate(CATEGORY_KEYWORDS.keys())
    }
    
    return [cluster_to_category[pred] for pred in predictions]