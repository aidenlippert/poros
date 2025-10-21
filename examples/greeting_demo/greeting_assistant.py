import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import asyncio
from agent_web import Agent

st.set_page_config(page_title="Personalized Greeting Demo", page_icon="👋", layout="wide")

REGISTRY_URL = "http://127.0.0.1:8000"
BOOTSTRAP_NODE = ("127.0.0.1", 8480)

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
    st.session_state.agent_initialized = False
    st.session_state.logs = []

def add_log(message: str, level: str = "info"):
    """Add a log message to the session state"""
    st.session_state.logs.append({
        "message": message,
        "level": level
    })

async def initialize_agent():
    """Initialize the Agent Web agent"""
    if not st.session_state.agent_initialized:
        try:
            add_log("🚀 Initializing Personal Assistant Agent...", "info")
            agent = Agent(
                registry_url=REGISTRY_URL,
                key_file="greeting_assistant.key",
                demo_mode=True
            )

            http_host = "127.0.0.1"
            http_port = 8022
            dht_host = "127.0.0.1"
            dht_port = 8492
            bootstrap_node = ("127.0.0.1", 8480)

            listen_task = asyncio.create_task(
                agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
            )
            await asyncio.sleep(2)

            await agent.register(
                public_endpoint=f"http://{http_host}:{http_port}",
                capabilities=["greeting_assistant"],
                price=0.0,
                payment_method="free"
            )

            st.session_state.agent = agent
            st.session_state.agent_initialized = True
            st.session_state.listen_task = listen_task
            add_log(f"✅ Personal Assistant Agent initialized", "success")
            add_log(f"   DID: {agent.did[:30]}...", "info")
            add_log(f"   HTTP: {http_host}:{http_port}", "info")
            return True
        except Exception as e:
            add_log(f"❌ Failed to initialize agent: {str(e)}", "error")
            import traceback
            add_log(f"   Details: {traceback.format_exc()}", "error")
            return False
    return True

async def create_personalized_greeting(name: str):
    """
    Create a personalized greeting by:
    1. Asking DayAgent for current day
    2. Asking GreetingAgent to create the greeting message
    """
    agent = st.session_state.agent

    try:
        # Step 1: Get the current day from DayAgent
        add_log(f"📅 Step 1: Need to know the current day...", "info")
        add_log(f"🔍 Discovering agents with 'day_service' capability...", "info")

        day_response = await agent.execute_task(
            capability="day_service",
            message_body={}
        )

        if day_response.get("status") != "success":
            add_log(f"❌ Failed to get day: {day_response}", "error")
            return None

        current_day = day_response.get("day")
        add_log(f"✅ Day Agent responded: It's {current_day}!", "success")

        # Step 2: Create personalized greeting
        add_log(f"💬 Step 2: Creating personalized greeting...", "info")
        add_log(f"🔍 Discovering agents with 'greeting_service' capability...", "info")

        greeting_response = await agent.execute_task(
            capability="greeting_service",
            message_body={
                "name": name,
                "day": current_day
            }
        )

        if greeting_response.get("status") != "success":
            add_log(f"❌ Failed to create greeting: {greeting_response}", "error")
            return None

        greeting = greeting_response.get("greeting")
        add_log(f"✅ Greeting Agent responded: '{greeting}'", "success")

        return greeting

    except Exception as e:
        add_log(f"❌ Error during agent communication: {str(e)}", "error")
        return None

# Main UI
st.title("👋 Personalized Greeting Demo")
st.markdown("**Demonstrating Multi-Agent Communication on Agent Web**")

st.markdown("""
This demo proves agent-to-agent communication:
1. **Personal Assistant** (this app) needs to create a personalized greeting
2. It asks **Day Agent** for the current day of the week
3. It then asks **Greeting Agent** to create the final greeting message

All communication happens through Agent Web's decentralized protocol (DID + DHT + P2P).
""")

# User input
col1, col2 = st.columns([3, 1])
with col1:
    name = st.text_input("Enter your name:", value="Aiden", placeholder="Your name here")
with col2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    create_button = st.button("Create Greeting", type="primary", use_container_width=True)

# Initialize agent on first run
if not st.session_state.agent_initialized:
    with st.spinner("Initializing Personal Assistant Agent..."):
        asyncio.run(initialize_agent())

# Handle greeting creation
if create_button and name:
    st.session_state.logs = []  # Clear previous logs
    add_log(f"🎯 User requested greeting for: {name}", "info")

    with st.spinner("Creating personalized greeting..."):
        greeting = asyncio.run(create_personalized_greeting(name))

    if greeting:
        st.success("🎉 **Greeting Created!**")
        st.markdown(f"### {greeting}")
    else:
        st.error("Failed to create greeting. Check the logs below.")

# Display logs
if st.session_state.logs:
    st.markdown("---")
    st.markdown("### 📋 Agent Communication Log")
    st.markdown("*Watch the agents talk to each other:*")

    for log in st.session_state.logs:
        if log["level"] == "info":
            st.info(log["message"])
        elif log["level"] == "success":
            st.success(log["message"])
        elif log["level"] == "error":
            st.error(log["message"])

# Sidebar with system status
with st.sidebar:
    st.markdown("### System Status")
    if st.session_state.agent_initialized:
        st.success("✅ Personal Assistant: Online")
        st.info(f"Port: {st.session_state.agent.port if st.session_state.agent else 'N/A'}")
    else:
        st.warning("⏳ Personal Assistant: Initializing...")

    st.markdown("---")
    st.markdown("### Expected Agents")
    st.markdown("""
    - **Day Agent** (day_service)
    - **Greeting Agent** (greeting_service)

    Make sure these agents are running!
    """)

    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("""
    ```
    [User]
      ↓
    [Personal Assistant]
      ↓ execute_task(day_service)
    [Day Agent] → returns day
      ↓
    [Personal Assistant]
      ↓ execute_task(greeting_service)
    [Greeting Agent] → returns greeting
      ↓
    [User sees result]
    ```
    """)
