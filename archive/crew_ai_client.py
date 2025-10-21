# crew_ai_client.py
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
from crewai import Agent as CrewAgent, Task, Crew

async def main():
    # 1. Setup our Agent Web "Phone"
    customer_agent = Agent(
        agent_id="crewai_customer",
        registry_url="http://127.0.0.1:8000",
        key_file="crewai.key",
        default_policy={'price': 0.7, 'reputation': 0.3}
    )

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

    # Create the CrewAI agent
    researcher = CrewAgent(
      role='Text Analyst',
      goal='Analyze texts to find their word and character counts.',
      backstory='You are an expert analyst who uses a network of other agents to get work done.',
      tools=[agent_web_tool],
      verbose=True,
      allow_delegation=False
    )

    # 4. Run the Test
    print("\n--- Sending request from CREWAI Agent ---")
    my_text = "This is a different test, this time from a CrewAI agent. It should also find the same service."

    # Create the task
    task = Task(
      description=f"Analyze the following text: '{my_text}'",
      expected_output='A JSON object with the word_count, char_count, and is_long_form status.',
      agent=researcher
    )

    # Create and kick off the crew
    crew = Crew(
      agents=[researcher],
      tasks=[task],
      verbose=2
    )

    # CrewAI's .kickoff() is synchronous, so we run it
    result = crew.kickoff()

    print("\n--- CrewAI Final Answer ---")
    print(result)

    listen_task.cancel()

if __name__ == "__main__":
    # Run in Terminal 4
    # Make sure OPENAI_API_KEY is set
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down CrewAI client")