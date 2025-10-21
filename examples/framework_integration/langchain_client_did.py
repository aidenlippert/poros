# langchain_client_did.py
import asyncio
from agent_web import Agent # Our SDK

# --- LangChain Tool Definition ---
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any

class AgentWebInput(BaseModel):
    capability: str = Field(description="The specific capability you are looking for. e.g., 'text_analyzer'")
    message_body: Dict[str, Any] = Field(description="The JSON payload for the task. e.g., {'text': '...'}")

class AgentWebExecutorTool(BaseTool):
    """A tool to find and use other agents on the decentralized Agent Web."""
    name: str = "agent_web_executor"
    description: str = "Use this to execute tasks on the Agent Web. Provide the 'capability' and 'message_body'."
    args_schema: Type[BaseModel] = AgentWebInput
    agent: Agent # Our SDK's Agent object

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Use '_arun' for async.")

    async def _arun(self, capability: str, message_body: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the task using our SDK's economic decision engine."""
        print(f"\n[LangChain Tool] Searching for '{capability}' on Agent Web")
        return await self.agent.execute_task(capability=capability, message_body=message_body)
# --- End of Tool Definition ---


# --- LangChain Agent Setup ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
import os

async def main():
    # 1. Setup our Agent Web "Phone" with DID-based identity
    # This agent is a customer, its policy is to just find the best deal
    customer_agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="langchain_did.key", # This file IS the identity
        default_policy={'price': 0.7, 'reputation': 0.3} # Prefers low price
    )

    print(f"[LangChain] Initialized with DID: {customer_agent.did}")

    # 2. Join the network in the background
    bootstrap_node = ("127.0.0.1", 8480) # The Service Agent's DHT
    listen_task = asyncio.create_task(
        customer_agent.listen_and_join(
            http_host="127.0.0.1", http_port=8011,
            dht_host="127.0.0.1", dht_port=8481,
            bootstrap_node=bootstrap_node
        )
    )
    await asyncio.sleep(2) # Give it time to join

    # 3. Setup the LangChain "Brain" with Gemini
    # Use environment variable or the provided key
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBFivYZYWSfBiWVGrLPU0Pr-JJs2Ffk4Pk")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0
        )
        print("[LangChain] Using Gemini 1.5 Flash model")
    except Exception as e:
        print(f"[LangChain] Error initializing Gemini: {e}")
        # Try gemini-pro as fallback
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0
        )
        print("[LangChain] Using Gemini Pro model")

    tools = [AgentWebExecutorTool(agent=customer_agent)]

    # Create a simple prompt for the agent
    from langchain_core.prompts import PromptTemplate

    prompt = PromptTemplate.from_template("""You are an assistant with access to tools.

Available tools:
{tools}

Tool Names: {tool_names}

When you need to use a tool, respond with:
Action: tool_name
Action Input: {{"capability": "...", "message_body": {{...}}}}

{agent_scratchpad}

    # 4. Run the Test
    print("\n--- Sending request from LANGCHAIN Agent ---")
    my_text = "This is a test to prove that our decentralized Agent Web works perfectly for cross-framework interoperability with unforgeable DID-based identity!"
    response = await agent_executor.ainvoke({
        "input": f"Please analyze the following text: '{my_text}'"
    })

    print("\n--- LangChain Final Answer ---")
    print(response['output'])

    listen_task.cancel()

if __name__ == "__main__":
    # Run in Terminal 3
    # Make sure GOOGLE_API_KEY is set
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down LangChain client")