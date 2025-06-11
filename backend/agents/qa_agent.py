from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI
llm = ChatOpenAI(
    model_name="gpt-4-turbo-preview",
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY
)

class SpendSummaryInput(BaseModel):
    user_id: str = Field(..., description="User ID to get spending summary for")

class AffordabilityInput(BaseModel):
    monthly_payment: float = Field(..., description="Monthly payment amount to check")
    user_id: str = Field(..., description="User ID to check income against")

class SpendSummaryTool(BaseTool):
    name = "spend_summary"
    description = "Get spending summary for the last 3 months by category"
    args_schema = SpendSummaryInput

    def _run(self, user_id: str) -> str:
        try:
            # TODO: Replace with actual database query
            # This is a placeholder that should be replaced with actual data retrieval
            from ..models import Transaction
            from ..database import SessionLocal
            
            db = SessionLocal()
            three_months_ago = datetime.now() - timedelta(days=90)
            
            # Get transactions for last 3 months
            transactions = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.date >= three_months_ago
            ).all()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': t.date,
                'amount': t.amount,
                'category': t.category
            } for t in transactions])
            
            if df.empty:
                return json.dumps({"error": "No transactions found"})
            
            # Calculate monthly summaries
            df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
            monthly_summary = df.groupby(['month', 'category'])['amount'].sum().unstack()
            
            # Calculate 3-month averages
            avg_by_category = df.groupby('category')['amount'].mean()
            
            summary = {
                "monthly_breakdown": monthly_summary.to_dict(),
                "category_averages": avg_by_category.to_dict(),
                "total_spending": df['amount'].sum(),
                "period": "last_3_months"
            }
            
            return json.dumps(summary)
            
        except Exception as e:
            logger.error(f"Error in spend_summary tool: {str(e)}")
            return json.dumps({"error": str(e)})

class AffordabilityTool(BaseTool):
    name = "affordability_calc"
    description = "Calculate if a monthly payment is affordable based on debt-to-income ratio"
    args_schema = AffordabilityInput

    def _run(self, monthly_payment: float, user_id: str) -> str:
        try:
            # TODO: Replace with actual database query
            # This is a placeholder that should be replaced with actual data retrieval
            from ..models import Transaction, User
            from ..database import SessionLocal
            
            db = SessionLocal()
            
            # Get user's monthly income
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return json.dumps({"error": "User not found"})
            
            # Get current monthly debt payments
            current_month = datetime.now().replace(day=1)
            monthly_debt = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.date >= current_month,
                Transaction.category.in_(['Mortgage', 'Car Payment', 'Credit Card', 'Loan'])
            ).with_entities(func.sum(Transaction.amount)).scalar() or 0
            
            # Calculate debt-to-income ratio
            total_monthly_debt = monthly_debt + monthly_payment
            dti_ratio = (total_monthly_debt / user.monthly_income) * 100
            
            # Standard DTI thresholds
            is_affordable = dti_ratio <= 43  # Standard mortgage DTI limit
            
            result = {
                "current_monthly_debt": monthly_debt,
                "proposed_payment": monthly_payment,
                "total_monthly_debt": total_monthly_debt,
                "dti_ratio": round(dti_ratio, 2),
                "is_affordable": is_affordable,
                "monthly_income": user.monthly_income
            }
            
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error in affordability_calc tool: {str(e)}")
            return json.dumps({"error": str(e)})

# Initialize tools
tools = [
    SpendSummaryTool(),
    AffordabilityTool()
]

# Create prompt template
template = """You are a helpful financial advisor assistant. Use the following tools to answer the user's question:

{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation history:
{chat_history}

Question: {question}
{agent_scratchpad}"""

prompt = StringPromptTemplate(
    template=template,
    input_variables=["tools", "tool_names", "chat_history", "question", "agent_scratchpad"]
)

# Initialize memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Initialize agent
agent = LLMSingleActionAgent(
    llm_chain=llm,
    output_parser=None,  # Will be handled by the executor
    stop=["\nObservation:"],
    allowed_tools=[tool.name for tool in tools]
)

# Initialize agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)

def answer_question(question: str, user_id: str) -> str:
    """
    Answer a financial question using the QA agent.
    
    Args:
        question: The user's question
        user_id: The ID of the user asking the question
        
    Returns:
        str: The agent's answer
    """
    try:
        # Add user_id to the question context
        context = f"User ID: {user_id}\nQuestion: {question}"
        
        # Get response from agent
        response = agent_executor.run(context)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in answer_question: {str(e)}")
        return "I apologize, but I'm having trouble processing your question right now. Please try again later." 