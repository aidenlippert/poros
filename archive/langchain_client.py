# langchain_client.py
import asyncio
from agent_web import Agent # Our SDK

# --- LangChain Tool Definition ---
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
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
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

async def main():
    # 1. Setup our Agent Web "Phone"
    # This agent is a customer, its policy is to just find the best deal
    customer_agent = Agent(
        agent_id="langchain_customer",
        registry_url="http://127.0.0.1:8000",
        key_file="langchain.key",
        default_policy={'price': 0.7, 'reputation': 0.3} # Prefers low price
    )

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

    # 3. Setup the LangChain "Brain"
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = [AgentWebExecutorTool(agent=customer_agent)]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant. You must use your tools to accomplish tasks."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    langchain_agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=langchain_agent, tools=tools, verbose=True)

    # 4. Run the Test
    print("\n--- Sending request from LANGCHAIN Agent ---")
    my_text = "This is a test sentence. We want to see if LangChain can find the service."
    response = await agent_executor.ainvoke({
        "input": f"Please analyze the following text: '{my_text}'"
    })

    print("\n--- LangChain Final Answer ---")
    print(response['output'])

    listen_task.cancel()

if __name__ == "__main__":
    # Run in Terminal 3
    # Make sure OPENAI_API_KEY is set
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down LangChain client")