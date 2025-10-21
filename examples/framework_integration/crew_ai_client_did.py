# crew_ai_client_did.py
import asyncio
from agent_web import Agent # Our SDK

# --- CrewAI Tool Definition ---
# Note: CrewAI's tool definition is simpler than LangChain's
from crewai_tools import BaseTool
from typing import Dict, Any
import nest_asyncio

# Apply nest_asyncio to allow asyncio to run inside CrewAI's sync event loop
nest_asyncio.apply()

class CrewAIAgentWebTool(BaseTool):
    """A CrewAI tool to find and use other agents on the decentralized Agent Web."""
    name: str = "Agent Web Executor"
    description: str = "Use this to execute tasks on the Agent Web. Input must be a dictionary with 'capability' and 'message_body'."

    # We will pass our running Agent object into this tool
    agent: Agent

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Runs the task using our SDK's economic decision engine."""
        capability = kwargs.get("capability")
        message_body = kwargs.get("message_body")

        if not capability or not message_body:
            return {"error": "You must provide 'capability' and 'message_body' in the input."}

        print(f"\n[CrewAI Tool] Searching for '{capability}' on Agent Web")

        # We must run our async SDK function in the existing event loop
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.agent.execute_task(capability=capability, message_body=message_body)
        )
        return response
# --- End of Tool Definition ---


# --- CrewAI Agent Setup ---
from crewai import Agent as CrewAgent, Task, Crew, LLM
import os

async def main():
    # 1. Setup our Agent Web "Phone" with DID-based identity
    customer_agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="crewai_did.key", # This file IS the identity
        default_policy={'price': 0.7, 'reputation': 0.3}
    )

    print(f"[CrewAI] Initialized with DID: {customer_agent.did}")

    # 2. Join the network in the background
    bootstrap_node = ("127.0.0.1", 8480) # The Service Agent's DHT
    listen_task = asyncio.create_task(
        customer_agent.listen_and_join(
            http_host="127.0.0.1", http_port=8012,
            dht_host="127.0.0.1", dht_port=8482,
            bootstrap_node=bootstrap_node
        )
    )
    await asyncio.sleep(2) # Give it time to join

    # 3. Setup the CrewAI "Brain"
    # Create the tool instance
    agent_web_tool = CrewAIAgentWebTool(agent=customer_agent)

    # Initialize the Gemini LLM with environment variable or fallback key
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBFivYZYWSfBiWVGrLPU0Pr-JJs2Ffk4Pk")

    try:
        gemini_llm = LLM(
            model='gemini/gemini-1.5-flash',
            api_key=api_key,
        )
        print("[CrewAI] Using Gemini 1.5 Flash model")
    except Exception as e:
        print(f"[CrewAI] Error with Gemini Flash, trying Pro: {e}")
        # Fallback to gemini-pro
        gemini_llm = LLM(
            model='gemini/gemini-pro',
            api_key=api_key,
        )
        print("[CrewAI] Using Gemini Pro model")

    # Create the CrewAI agent
    researcher = CrewAgent(
      role='Text Analyst',
      goal='Analyze texts to find their word and character counts using the Agent Web tool.',
      backstory='You are an expert analyst who uses a network of other agents to get work done.',
      tools=[agent_web_tool],
      llm=gemini_llm,
      verbose=True,
      allow_delegation=False
    )

    # 4. Run the Test
    print("\n--- Sending request from CREWAI Agent ---")
    my_text = "This is a test to prove that our decentralized Agent Web works perfectly for cross-framework interoperability with unforgeable DID-based identity!"

    # Create the task
    task = Task(
      description=f"Use the Agent Web Executor tool to analyze the following text. Pass capability='text_analyzer' and message_body={{'text': '{my_text}'}} to the tool.",
      expected_output='A JSON object with the word_count, char_count, and is_long_form status.',
      agent=researcher
    )

    # Create and kick off the crew
    crew = Crew(
      agents=[researcher],
      tasks=[task],
      verbose=True
    )

    # CrewAI's .kickoff() is synchronous, so we run it
    result = crew.kickoff()

    print("\n--- CrewAI Final Answer ---")
    print(result)

    listen_task.cancel()

if __name__ == "__main__":
    # Run in Terminal 4
    # Make sure GOOGLE_API_KEY is set
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down CrewAI client")