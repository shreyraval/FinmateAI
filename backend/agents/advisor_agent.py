from langchain.llms import OpenAI
from langchain.agents import initialize_agent, Tool

llm = OpenAI(temperature=0)
tools = [Tool(name="Spending Summary", func=lambda x: x, description="Analyzes spending")]

agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description")

def get_advice(input_text):
    return agent.run(input_text)
