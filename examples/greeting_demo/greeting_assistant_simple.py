import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import asyncio
from agent_web import Agent
import threading
import time
import re
from datetime import datetime

st.set_page_config(page_title="Agent Web Chat", page_icon="🤖", layout="wide")

# Global agent instance (singleton across all sessions)
_agent_instance = None
_agent_lock = threading.Lock()
_agent_ready = threading.Event()
_loop_container = {}

def get_or_create_agent():
    """Get or create the singleton agent instance"""
    global _agent_instance, _loop_container

    with _agent_lock:
        if _agent_instance is None:
            print("[INIT] Creating new agent instance...", flush=True)
            _agent_instance = Agent(
                registry_url="http://127.0.0.1:8000",
                key_file="greeting_assistant_simple.key",
                demo_mode=True
            )

            # Start background thread
            thread = threading.Thread(
                target=init_agent_background,
                args=(_agent_instance, _loop_container, _agent_ready),
                daemon=True
            )
            thread.start()
            print(f"[INIT] Agent DID: {_agent_instance.did[:40]}...", flush=True)
            print("[INIT] Background thread started", flush=True)

        return _agent_instance

def init_agent_background(agent, loop_container, ready_event):
    """Initialize agent in background thread - runs ONCE"""
    print("[BG] Background thread starting...", flush=True)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop_container["loop"] = loop

    http_host = "127.0.0.1"
    http_port = 8035
    dht_host = "127.0.0.1"
    dht_port = 8505
    bootstrap_node = ("127.0.0.1", 8480)

    async def setup():
        try:
            print(f"[BG] Starting network: HTTP={http_host}:{http_port}, DHT={dht_host}:{dht_port}", flush=True)

            asyncio.create_task(
                agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
            )

            await asyncio.sleep(2)

            print("[BG] Registering capabilities...", flush=True)
            await agent.register(
                public_endpoint=f"http://{http_host}:{http_port}",
                capabilities=["personal_assistant"],
                price=0.0,
                payment_method="free"
            )

            print(f"[BG] ✅ Agent ready! DID: {agent.did[:40]}...", flush=True)
            ready_event.set()

        except Exception as e:
            print(f"[BG] ❌ Setup error: {e}", flush=True)
            import traceback
            traceback.print_exc()

    try:
        loop.run_until_complete(setup())
        print("[BG] Event loop running forever...", flush=True)
        loop.run_forever()
    except Exception as e:
        print(f"[BG] ❌ Background thread error: {e}", flush=True)

# Initialize agent (once, globally)
agent = get_or_create_agent()

# Initialize session-specific state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Personal Assistant. I can help you with:\n\n- **Get the current day**: Ask 'What day is it?'\n- **Create greetings**: Say 'Greet me' or 'Hello, I'm [name]'\n\nI'll delegate tasks to specialized agents as needed!"}
    ]

if "agent_checked" not in st.session_state:
    st.session_state.agent_checked = False

# Check if agent is ready (non-blocking)
if not st.session_state.agent_checked:
    if _agent_ready.is_set():
        st.session_state.agent_checked = True
    else:
        # Still initializing, show message and rerun
        st.info("🔄 Initializing agent network... Please wait.")
        time.sleep(1)
        st.rerun()

def process_user_query(query: str):
    """Process user query using the global agent"""
    loop = _loop_container.get("loop")

    if not loop or loop.is_closed():
        return "❌ Agent not ready. Please refresh the page."

    query_lower = query.lower()

    async def handle_query():
        try:
            # Check for day query
            if any(word in query_lower for word in ["day", "date", "today", "what day"]):
                day_response = await agent.execute_task(
                    capability="day_service",
                    message_body={}
                )

                if day_response.get("status") == "success":
                    current_day = day_response.get("day")
                    return f"📅 **Agent Communication:**\n\n1. 🔎 Searched DHT for 'day_service'\n2. ✅ Found Day Agent\n3. 📡 Sent P2P message\n4. 📥 Received response\n\n**Result:** Today is **{current_day}**!"
                else:
                    return f"❌ Couldn't get the day: {day_response}"

            # Check for greeting request
            elif any(word in query_lower for word in ["greet", "hello", "hi", "greeting"]):
                # Extract name
                name = "Friend"
                name_match = re.search(r"(?:i'm|i am|my name is|call me)\s+(\w+)", query_lower)
                if name_match:
                    name = name_match.group(1).capitalize()
                elif "greet me" not in query_lower:
                    words = query.split()
                    if len(words) >= 2:
                        potential_name = words[-1].strip(".,!?")
                        if potential_name.isalpha():
                            name = potential_name.capitalize()

                # Step 1: Get day
                day_response = await agent.execute_task(
                    capability="day_service",
                    message_body={}
                )

                if day_response.get("status") != "success":
                    return f"❌ Couldn't get the day: {day_response}"

                current_day = day_response.get("day")

                # Step 2: Create greeting
                greeting_response = await agent.execute_task(
                    capability="greeting_service",
                    message_body={"name": name, "day": current_day}
                )

                if greeting_response.get("status") == "success":
                    greeting = greeting_response.get("greeting")
                    return f"💬 **Multi-Agent Orchestration:**\n\n**Step 1: Day Agent**\n- 🔎 DHT lookup: 'day_service'\n- ✅ Found agent\n- 📥 Response: {current_day}\n\n**Step 2: Greeting Agent**\n- 🔎 DHT lookup: 'greeting_service'\n- ✅ Found agent  \n- 📤 Sent: name={name}, day={current_day}\n- 📥 Response: {greeting}\n\n**Final Result:** {greeting}"
                else:
                    return f"❌ Couldn't create greeting: {greeting_response}"

            else:
                return "I'm not sure how to help with that. Try asking:\n- 'What day is it?'\n- 'Greet me' or 'Hello, I'm [Your Name]'"

        except Exception as e:
            import traceback
            return f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"

    # Submit to background loop
    future = asyncio.run_coroutine_threadsafe(handle_query(), loop)
    try:
        result = future.result(timeout=30)
        return result
    except Exception as e:
        return f"❌ Timeout or error: {str(e)}"

# Header
st.title("🤖 Agent Web Chat")
st.markdown("**Chat with your Personal Assistant - it delegates to specialized agents!**")

if st.session_state.agent_checked:
    st.success(f"✅ Personal Assistant Online | DID: {agent.did[:30]}...")
else:
    st.warning("🔄 Initializing...")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything...", disabled=not st.session_state.agent_checked):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process and respond
    with st.chat_message("assistant"):
        with st.spinner("🔍 Processing..."):
            response = process_user_query(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.markdown("### System Status")
    if st.session_state.agent_checked:
        st.success("✅ Personal Assistant: Online")
        st.info(f"DID: {agent.did[:20]}...")
        st.info("HTTP: 127.0.0.1:8035")
        st.info("DHT: 127.0.0.1:8505")
    else:
        st.warning("🔄 Initializing...")

    st.markdown("---")
    st.markdown("### Backend Agents")
    st.markdown("""
    - **Day Agent** (day_service)
      - HTTP: 127.0.0.1:8020
      - DHT: 127.0.0.1:8490
    - **Greeting Agent** (greeting_service)
      - HTTP: 127.0.0.1:8021
      - DHT: 127.0.0.1:8491
    """)

    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
    1. You send a message
    2. Personal Assistant analyzes it
    3. It searches DHT for needed capabilities
    4. It contacts specialist agents via P2P
    5. You get the combined result!
    """)

    st.markdown("---")
    st.markdown("### Try These")
    st.code("""
• "What day is it?"
• "Greet me"
• "Hello, I'm Aiden"
    """)

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! How can I help you?"}
        ]
        st.rerun()
