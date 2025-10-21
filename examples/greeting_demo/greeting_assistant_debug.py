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

st.set_page_config(page_title="Agent Web Debug Demo", page_icon="🔍", layout="wide")

DEBUG_LOG = []

def log_debug(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    DEBUG_LOG.append(f"[{timestamp}] {message}")
    print(f"[DEBUG {timestamp}] {message}", flush=True)

def init_agent_background(agent, loop_container, ready_event):
    """Initialize agent in background thread with detailed logging"""
    log_debug("🔧 Background thread started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop_container["loop"] = loop
    log_debug("✅ Event loop created")

    http_host = "127.0.0.1"
    http_port = 8030
    dht_host = "127.0.0.1"
    dht_port = 8500
    bootstrap_node = ("127.0.0.1", 8480)

    async def setup():
        try:
            log_debug(f"🌐 Starting HTTP server on {http_host}:{http_port}")
            log_debug(f"🔗 Starting DHT node on {dht_host}:{dht_port}")

            asyncio.create_task(
                agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
            )

            log_debug("⏳ Waiting 3 seconds for network setup...")
            await asyncio.sleep(2)

            log_debug(f"📝 Registering agent with capabilities: ['personal_assistant']")
            await agent.register(
                public_endpoint=f"http://{http_host}:{http_port}",
                capabilities=["personal_assistant"],
                price=0.0,
                payment_method="free"
            )

            log_debug(f"✅ Agent ready! DID: {agent.did[:30]}...")
            ready_event.set()

        except Exception as e:
            log_debug(f"❌ Setup error: {e}")
            import traceback
            log_debug(f"Traceback: {traceback.format_exc()}")
            loop_container["error"] = str(e)

    try:
        loop.run_until_complete(setup())
        log_debug("🔄 Event loop running forever...")
        loop.run_forever()
    except Exception as e:
        log_debug(f"❌ Background thread error: {e}")
        loop_container["error"] = str(e)

if 'agent_initialized' not in st.session_state:
    log_debug("🚀 Initializing session state")
    st.session_state.agent_initialized = False
    st.session_state.agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="greeting_assistant_debug.key",
        demo_mode=True
    )
    st.session_state.loop_container = {}
    st.session_state.ready_event = threading.Event()
    st.session_state.debug_logs = []

    log_debug(f"🆔 Agent DID: {st.session_state.agent.did[:30]}...")

    thread = threading.Thread(
        target=init_agent_background,
        args=(st.session_state.agent, st.session_state.loop_container, st.session_state.ready_event),
        daemon=True
    )
    thread.start()
    log_debug("🧵 Background thread launched")
    st.session_state.init_start_time = time.time()

# Check if initialization is complete (non-blocking)
if not st.session_state.agent_initialized:
    if st.session_state.ready_event.is_set():
        st.session_state.agent_initialized = True
        log_debug("✅ Agent initialization complete!")
    elif time.time() - st.session_state.init_start_time > 15:
        log_debug("❌ Agent initialization timeout!")
        st.session_state.agent_initialized = False
    else:
        # Still waiting, rerun to check again
        time.sleep(0.5)
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🔍 **Debug Mode Active**\n\nI'm your Personal Assistant with detailed logging. I can:\n\n- **Get the current day**: Ask 'What day is it?'\n- **Create greetings**: Say 'Greet me' or 'Hello, I'm [name]'\n\nWatch the debug panel to see agent discovery and communication!"}
    ]

def process_user_query(query: str):
    """Process user query with detailed logging"""
    agent = st.session_state.agent
    loop = st.session_state.loop_container.get("loop")

    if not loop:
        return "❌ Agent not ready yet, please wait..."

    if loop.is_closed():
        return "❌ Event loop is closed. Please refresh the page."

    query_lower = query.lower()
    log_debug(f"📨 Processing query: '{query}'")

    async def handle_query():
        try:
            # Check for day query
            if any(word in query_lower for word in ["day", "date", "today", "what day"]):
                log_debug("🔍 Query type: DAY_SERVICE")
                log_debug("🔎 Searching DHT for capability: 'day_service'")

                day_response = await agent.execute_task(
                    capability="day_service",
                    message_body={}
                )

                log_debug(f"📥 Day Agent response: {day_response}")

                if day_response.get("status") == "success":
                    current_day = day_response.get("day")
                    log_debug(f"✅ Got day from agent: {current_day}")
                    return f"📅 **Agent Discovery & Communication Log:**\n\n1️⃣ Searched DHT for 'day_service' capability\n2️⃣ Found Day Agent\n3️⃣ Established P2P connection\n4️⃣ Received response\n\n✅ Today is **{current_day}**!"
                else:
                    log_debug(f"❌ Day service failed: {day_response}")
                    return f"❌ Sorry, couldn't get the day: {day_response}"

            # Check for greeting request
            elif any(word in query_lower for word in ["greet", "hello", "hi", "greeting"]):
                log_debug("🔍 Query type: GREETING_SERVICE (multi-agent)")

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

                log_debug(f"👤 Extracted name: {name}")

                # Step 1: Get day
                log_debug("📡 STEP 1: Contacting Day Agent")
                log_debug("🔎 Searching DHT for 'day_service'")

                day_response = await agent.execute_task(
                    capability="day_service",
                    message_body={}
                )

                log_debug(f"📥 Day Agent response: {day_response}")

                if day_response.get("status") != "success":
                    log_debug(f"❌ Day service failed")
                    return f"❌ Couldn't get the day: {day_response}"

                current_day = day_response.get("day")
                log_debug(f"✅ Got day: {current_day}")

                # Step 2: Create greeting
                log_debug("📡 STEP 2: Contacting Greeting Agent")
                log_debug("🔎 Searching DHT for 'greeting_service'")
                log_debug(f"📤 Sending: name={name}, day={current_day}")

                greeting_response = await agent.execute_task(
                    capability="greeting_service",
                    message_body={"name": name, "day": current_day}
                )

                log_debug(f"📥 Greeting Agent response: {greeting_response}")

                if greeting_response.get("status") == "success":
                    greeting = greeting_response.get("greeting")
                    log_debug(f"✅ Got greeting: {greeting}")
                    return f"💬 **Multi-Agent Orchestration Log:**\n\n**STEP 1: Day Agent**\n1️⃣ Searched DHT for 'day_service'\n2️⃣ Found agent\n3️⃣ Response: {current_day}\n\n**STEP 2: Greeting Agent**\n1️⃣ Searched DHT for 'greeting_service'\n2️⃣ Found agent\n3️⃣ Sent: name={name}, day={current_day}\n4️⃣ Response: {greeting}\n\n✅ **Result:** {greeting}"
                else:
                    log_debug(f"❌ Greeting service failed")
                    return f"❌ Couldn't create greeting: {greeting_response}"

            else:
                log_debug("❓ Query type: UNKNOWN")
                return "I'm not sure how to help with that. Try asking:\n- 'What day is it?'\n- 'Greet me' or 'Hello, I'm [Your Name]'"

        except Exception as e:
            log_debug(f"❌ Error: {str(e)}")
            import traceback
            log_debug(f"Traceback: {traceback.format_exc()}")
            return f"❌ Error: {str(e)}"

    # Submit to background loop and wait for result
    log_debug("🔀 Submitting coroutine to background event loop")
    future = asyncio.run_coroutine_threadsafe(handle_query(), loop)
    try:
        result = future.result(timeout=30)
        log_debug("✅ Query processing complete")
        return result
    except Exception as e:
        log_debug(f"❌ Timeout or error: {str(e)}")
        return f"❌ Timeout or error: {str(e)}"

# Header
st.title("🔍 Agent Web Debug Demo")
st.markdown("**Watch agent discovery and P2P communication in real-time!**")

col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.agent_initialized:
        st.success(f"✅ Personal Assistant Online | DID: {st.session_state.agent.did[:30]}...")
    else:
        st.warning("🔄 Initializing Personal Assistant...")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything...", disabled=not st.session_state.agent_initialized):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process and respond
        with st.chat_message("assistant"):
            with st.spinner("🔍 Processing with detailed logging..."):
                response = process_user_query(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    st.markdown("### 🔍 Debug Console")

    debug_container = st.container()
    with debug_container:
        if DEBUG_LOG:
            st.code("\n".join(DEBUG_LOG[-30:]), language="log")
        else:
            st.info("No debug logs yet")

    if st.button("🔄 Refresh Logs"):
        st.rerun()

    if st.button("🗑️ Clear Logs"):
        DEBUG_LOG.clear()
        st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### System Status")
    if st.session_state.agent_initialized:
        st.success("✅ Personal Assistant: Online")
        st.info(f"DID: {st.session_state.agent.did[:20]}...")
        st.info(f"HTTP: 127.0.0.1:8030")
        st.info(f"DHT: 127.0.0.1:8500")
    else:
        st.warning("🔄 Initializing...")

    st.markdown("---")
    st.markdown("### Expected Backend Agents")
    st.markdown("""
    - **Day Agent** (day_service)
      - HTTP: 127.0.0.1:8020
      - DHT: 127.0.0.1:8490
    - **Greeting Agent** (greeting_service)
      - HTTP: 127.0.0.1:8021
      - DHT: 127.0.0.1:8491
    """)

    st.markdown("---")
    st.markdown("### Debug Features")
    st.markdown("""
    ✅ DHT discovery logging
    ✅ P2P connection tracking
    ✅ Message payload inspection
    ✅ Response validation
    ✅ Multi-agent orchestration
    """)

    st.markdown("---")
    st.markdown("### Try These Queries")
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
