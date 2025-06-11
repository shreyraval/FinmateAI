import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import openai
from openai import OpenAI
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_budget_advice(df: pd.DataFrame) -> str:
    """
    Analyze spending patterns and generate personalized financial advice.
    
    Args:
        df: DataFrame with columns [date, description, amount, category]
        
    Returns:
        str: Personalized financial advice
    """
    try:
        # Ensure required columns
        required_cols = ['date', 'amount', 'category']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
        # Convert date to datetime if not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Get spending analysis
        spending_summary = _analyze_spending(df)
        anomalies = _detect_spending_anomalies(df)
        
        # Generate advice using OpenAI
        advice = _generate_advice(spending_summary, anomalies)
        
        return advice
        
    except Exception as e:
        logger.error(f"Error generating budget advice: {str(e)}")
        return "I apologize, but I'm having trouble analyzing your spending patterns right now. Please try again later."

def _analyze_spending(df: pd.DataFrame) -> Dict:
    """Analyze spending patterns by category and time period."""
    # Get current month's data
    current_month = df['date'].max().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # Calculate monthly totals by category
    current_month_spending = df[df['date'] >= current_month].groupby('category')['amount'].sum()
    last_month_spending = df[(df['date'] >= last_month) & (df['date'] < current_month)].groupby('category')['amount'].sum()
    
    # Calculate overall totals
    total_current = current_month_spending.sum()
    total_last = last_month_spending.sum()
    
    # Calculate category percentages
    current_percentages = (current_month_spending / total_current * 100).round(1)
    last_percentages = (last_month_spending / total_last * 100).round(1)
    
    return {
        'current_month': current_month.strftime('%B %Y'),
        'last_month': last_month.strftime('%B %Y'),
        'current_totals': current_month_spending.to_dict(),
        'last_totals': last_month_spending.to_dict(),
        'current_percentages': current_percentages.to_dict(),
        'last_percentages': last_percentages.to_dict(),
        'total_current': total_current,
        'total_last': total_last
    }

def _detect_spending_anomalies(df: pd.DataFrame) -> List[Dict]:
    """Detect significant spending changes between months."""
    anomalies = []
    
    # Get monthly data
    df['month'] = df['date'].dt.to_period('M')
    monthly_by_category = df.groupby(['month', 'category'])['amount'].sum().unstack()
    
    # Calculate month-over-month changes
    monthly_changes = monthly_by_category.pct_change() * 100
    
    # Get the most recent month's changes
    latest_changes = monthly_changes.iloc[-1]
    
    # Detect significant changes (>25% increase or decrease)
    for category, change in latest_changes.items():
        if abs(change) > 25:
            anomalies.append({
                'category': category,
                'change': round(change, 1),
                'direction': 'increase' if change > 0 else 'decrease'
            })
    
    return anomalies

def _generate_advice(spending_summary: Dict, anomalies: List[Dict]) -> str:
    """Generate personalized financial advice using OpenAI."""
    
    # Prepare the analysis for the prompt
    analysis = {
        'current_month': spending_summary['current_month'],
        'last_month': spending_summary['last_month'],
        'total_spending': {
            'current': round(spending_summary['total_current'], 2),
            'last': round(spending_summary['total_last'], 2),
            'change': round((spending_summary['total_current'] - spending_summary['total_last']) / spending_summary['total_last'] * 100, 1)
        },
        'top_categories': dict(sorted(spending_summary['current_percentages'].items(), key=lambda x: x[1], reverse=True)[:3]),
        'anomalies': anomalies
    }
    
    # Create the prompt
    prompt = f"""As a friendly Certified Financial Planner (CFP), analyze this spending data and provide personalized advice:

Current Month: {analysis['current_month']}
Last Month: {analysis['last_month']}

Total Spending:
- Current: ${analysis['total_spending']['current']}
- Last Month: ${analysis['total_spending']['last']}
- Change: {analysis['total_spending']['change']}%

Top Spending Categories:
{chr(10).join(f'- {cat}: {pct}%' for cat, pct in analysis['top_categories'].items())}

Notable Changes:
{chr(10).join(f'- {a["category"]}: {a["direction"]} of {abs(a["change"])}%' for a in analysis['anomalies'])}

Please provide:
1. A brief analysis of their spending patterns
2. One specific, actionable piece of advice
3. A positive, encouraging tone
4. Keep it under 3 sentences

Format the response as a friendly, conversational message."""

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a friendly, encouraging financial advisor who provides concise, actionable advice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return "I apologize, but I'm having trouble generating personalized advice right now. Please try again later."
