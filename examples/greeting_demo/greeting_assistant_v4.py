import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import asyncio
from agent_web import Agent
import threading
import time

st.set_page_config(page_title="Personalized Greeting Demo", page_icon="👋", layout="wide")

@st.cache_resource
def get_agent():
    """Create and initialize the agent in a separate thread"""
    agent_container = {"agent": None, "ready": False, "error": None}

    def init_agent():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            agent = Agent(
                registry_url="http://127.0.0.1:8000",
                key_file="greeting_assistant_v4.key",
                demo_mode=True
            )

            http_host = "127.0.0.1"
            http_port = 8025
            dht_host = "127.0.0.1"
            dht_port = 8495
            bootstrap_node = ("127.0.0.1", 8480)

            async def setup():
                try:
                    listen_task = asyncio.create_task(
                        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
                    )
                    await asyncio.sleep(3)

                    await agent.register(
                        public_endpoint=f"http://{http_host}:{http_port}",
                        capabilities=["greeting_assistant_v4"],
                        price=0.0,
                        payment_method="free"
                    )

                    agent_container["agent"] = agent
                    agent_container["ready"] = True

                except Exception as e:
                    agent_container["error"] = str(e)
                    raise

            loop.run_until_complete(setup())

        except Exception as e:
            agent_container["error"] = str(e)

    thread = threading.Thread(target=init_agent, daemon=True)
    thread.start()
    thread.join(timeout=10)

    if agent_container["error"]:
        raise Exception(f"Agent initialization failed: {agent_container['error']}")

    if not agent_container["ready"]:
        raise Exception("Agent initialization timeout")

    return agent_container["agent"]

if "logs" not in st.session_state:
    st.session_state.logs = []

def add_log(message: str, level: str = "info"):
    st.session_state.logs.append({"message": message, "level": level})

def create_greeting_sync(agent, name: str):
    """Synchronous wrapper for async greeting creation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def create():
        try:
            add_log("📅 Step 1: Asking Day Agent for current day...", "info")
            day_response = await agent.execute_task(
                capability="day_service",
                message_body={}
            )

            if day_response.get("status") != "success":
                add_log(f"❌ Day Agent failed: {day_response}", "error")
                return None

            current_day = day_response.get("day")
            add_log(f"✅ Day Agent responded: {current_day}", "success")

            add_log("💬 Step 2: Asking Greeting Agent to create message...", "info")
            greeting_response = await agent.execute_task(
                capability="greeting_service",
                message_body={"name": name, "day": current_day}
            )

            if greeting_response.get("status") != "success":
                add_log(f"❌ Greeting Agent failed: {greeting_response}", "error")
                return None

            greeting = greeting_response.get("greeting")
            add_log(f"✅ Greeting Agent responded: '{greeting}'", "success")
            return greeting

        except Exception as e:
            add_log(f"❌ Error: {str(e)}", "error")
            return None

    result = loop.run_until_complete(create())
    loop.close()
    return result

st.title("👋 Personalized Greeting Demo")
st.markdown("**Demonstrating Multi-Agent Communication on Agent Web**")

st.markdown("""
This demo proves agent-to-agent communication:
1. **Personal Assistant** (this app) needs to create a personalized greeting
2. It asks **Day Agent** for the current day of the week
3. It then asks **Greeting Agent** to create the final greeting message

All communication happens through Agent Web's decentralized protocol (DID + DHT + P2P).
""")

try:
    with st.spinner("Initializing Personal Assistant Agent..."):
        agent = get_agent()
    st.success(f"✅ Agent initialized! DID: {agent.did[:30]}...")
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

col1, col2 = st.columns([3, 1])
with col1:
    name = st.text_input("Enter your name:", value="Aiden")
with col2:
    st.write("")
    st.write("")
    create_button = st.button("Create Greeting", type="primary", use_container_width=True)

if create_button and name:
    st.session_state.logs = []
    add_log(f"🎯 Creating greeting for: {name}", "info")

    with st.spinner("Creating personalized greeting..."):
        greeting = create_greeting_sync(agent, name)

    if greeting:
        st.success("🎉 **Greeting Created!**")
        st.markdown(f"### {greeting}")
    else:
        st.error("Failed to create greeting. Check logs below.")

if st.session_state.logs:
    st.markdown("---")
    st.markdown("### 📋 Agent Communication Log")
    for log in st.session_state.logs:
        if log["level"] == "info":
            st.info(log["message"])
        elif log["level"] == "success":
            st.success(log["message"])
        elif log["level"] == "error":
            st.error(log["message"])

with st.sidebar:
    st.markdown("### System Status")
    st.success("✅ Personal Assistant: Online")
    st.info(f"DID: {agent.did[:20]}...")

    st.markdown("---")
    st.markdown("### Expected Agents")
    st.markdown("""
    - **Day Agent** (day_service)
    - **Greeting Agent** (greeting_service)
    """)

    st.markdown("---")
    st.markdown("### Architecture")
    st.code("""
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
    """)
