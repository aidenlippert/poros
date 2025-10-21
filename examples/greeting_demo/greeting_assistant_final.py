import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import asyncio
from agent_web import Agent
import threading
import time
import re

st.set_page_config(page_title="Agent Web Chat Demo", page_icon="🤖", layout="wide")

def init_agent_background(agent, loop_container):
    """Initialize agent in background thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop_container["loop"] = loop

    http_host = "127.0.0.1"
    http_port = 8028
    dht_host = "127.0.0.1"
    dht_port = 8498
    bootstrap_node = ("127.0.0.1", 8480)

    async def setup():
        asyncio.create_task(
            agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
        )
        await asyncio.sleep(3)

        await agent.register(
            public_endpoint=f"http://{http_host}:{http_port}",
            capabilities=["personal_assistant"],
            price=0.0,
            payment_method="free"
        )

        print(f"✅ Agent ready: {agent.did[:30]}...")

    try:
        loop.run_until_complete(setup())
        # Keep loop running forever
        loop.run_forever()
    except Exception as e:
        print(f"Agent error: {e}")
    finally:
        loop.close()

if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
    st.session_state.agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="greeting_assistant_final.key",
        demo_mode=True
    )
    st.session_state.loop_container = {}

    thread = threading.Thread(
        target=init_agent_background,
        args=(st.session_state.agent, st.session_state.loop_container),
        daemon=True
    )
    thread.start()
    time.sleep(4)
    st.session_state.agent_initialized = True

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Personal Assistant. I can help you with:\n\n- **Get the current day**: Ask 'What day is it?'\n- **Create greetings**: Say 'Greet me' or 'Hello, I'm [name]'\n\nI'll delegate tasks to specialized agents as needed!"}
    ]

def process_user_query(query: str):
    """Process user query using the background event loop"""
    agent = st.session_state.agent
    loop = st.session_state.loop_container.get("loop")

    if not loop:
        return "❌ Agent not ready yet, please wait..."

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
                    return f"📅 Asked Day Agent...\n\n✅ Today is **{current_day}**!"
                else:
                    return f"❌ Sorry, couldn't get the day: {day_response}"

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
                    return f"💬 Creating greeting for **{name}**...\n\n📅 Day Agent says: **{current_day}**\n\n✅ Greeting Agent says: **{greeting}**"
                else:
                    return f"❌ Couldn't create greeting: {greeting_response}"

            else:
                return "I'm not sure how to help with that. Try asking:\n- 'What day is it?'\n- 'Greet me' or 'Hello, I'm [Your Name]'"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    # Submit to background loop and wait for result
    future = asyncio.run_coroutine_threadsafe(handle_query(), loop)
    try:
        result = future.result(timeout=30)
        return result
    except Exception as e:
        return f"❌ Timeout or error: {str(e)}"

# Header
st.title("🤖 Agent Web Chat Demo")
st.markdown("**Chat with your Personal Assistant - it delegates to other agents!**")

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
        with st.spinner("Thinking..."):
            response = process_user_query(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.markdown("### System Status")
    if st.session_state.agent_initialized:
        st.success("✅ Personal Assistant: Online")
        st.info(f"DID: {st.session_state.agent.did[:20]}...")
    else:
        st.warning("🔄 Initializing...")

    st.markdown("---")
    st.markdown("### Available Agents")
    st.markdown("""
    - **Day Agent** (day_service)
    - **Greeting Agent** (greeting_service)
    """)

    st.markdown("---")
    st.markdown("### Try These Queries")
    st.code("""
• "What day is it?"
• "Greet me"
• "Hello, I'm Aiden"
• "Create a greeting for me"
    """)

    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown("""
    1. You send a message
    2. Personal Assistant analyzes it
    3. It discovers needed agents via DHT
    4. It delegates tasks to specialists
    5. You get the combined result!
    """)

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! How can I help you?"}
        ]
        st.rerun()
