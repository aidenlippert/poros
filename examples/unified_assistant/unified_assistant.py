import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import asyncio
import json
import time
import re
from typing import Tuple, Dict, Any, Optional
from agent_web import Agent

st.set_page_config(page_title="Your Personal AI Assistant", page_icon="🤖", layout="wide")

REGISTRY_URL = "http://127.0.0.1:8000"
BOOTSTRAP_NODE = ("127.0.0.1", 8480)

USER_PROFILE = {
    "name": "Alex Johnson",
    "location": "San Francisco, CA",
    "dietary_restrictions": ["vegetarian"],
    "preferred_price": "$$",
    "payment_method": "Visa •••• 4242",
    "default_party_size": 2
}

@st.cache_resource
def init_agent():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    agent = Agent(
        registry_url=REGISTRY_URL,
        key_file="unified_assistant.key",
        default_policy={'price': 0.3, 'reputation': 0.7},
        demo_mode=True
    )

    async def start_agent():
        listen_task = asyncio.create_task(
            agent.listen_and_join(
                http_host="127.0.0.1", http_port=8019,
                dht_host="127.0.0.1", dht_port=8489,
                bootstrap_node=BOOTSTRAP_NODE
            )
        )
        await asyncio.sleep(2)

        await agent.register(
            public_endpoint="http://127.0.0.1:8019",
            capabilities=["personal_assistant_client"],
            price=0.0,
            payment_method="free"
        )
        return listen_task

    listen_task = loop.run_until_complete(start_agent())
    return agent, loop

agent, event_loop = init_agent()

def parse_intent(user_input: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    text = user_input.lower()

    flight_keywords = ["flight", "fly", "airline", "plane", "ticket"]
    restaurant_keywords = ["restaurant", "food", "eat", "dinner", "lunch", "sushi", "italian", "mexican", "japanese"]

    if any(kw in text for kw in flight_keywords):
        destination = "SFO"
        date = "Monday"

        dest_match = re.search(r'(?:from\s+\w+\s+)?to\s+([A-Z]{3}|\w+)', text, re.IGNORECASE)
        if dest_match:
            destination = dest_match.group(1).strip().upper()[:3]

        date_match = re.search(r'(?:on\s+)?(\w+day)', text, re.IGNORECASE)
        if date_match:
            date = date_match.group(1).capitalize()

        return "travel_booking", {
            "task": "find_flight",
            "destination": destination,
            "date": date
        }

    elif any(kw in text for kw in restaurant_keywords):
        cuisine = "italian"

        if "mexican" in text:
            cuisine = "mexican"
        elif "japanese" in text or "sushi" in text:
            cuisine = "japanese"
        elif "italian" in text:
            cuisine = "italian"

        return "restaurant_booking", {
            "action": "search",
            "cuisine": cuisine,
            "price_preference": USER_PROFILE["preferred_price"],
            "party_size": USER_PROFILE["default_party_size"]
        }

    return None

st.title("🤖 Your Personal AI Assistant")
st.caption(f"Hello, {USER_PROFILE['name']}! • Powered by Agent Web")

col1, col2 = st.columns([2, 1])

with col2:
    with st.expander("👤 Your Profile", expanded=True):
        st.write(f"**Name:** {USER_PROFILE['name']}")
        st.write(f"**Location:** {USER_PROFILE['location']}")
        st.write(f"**Dietary:** {', '.join(USER_PROFILE['dietary_restrictions'])}")
        st.write(f"**Price Pref:** {USER_PROFILE['preferred_price']}")
        st.write(f"**Payment:** {USER_PROFILE['payment_method']}")

    with st.expander("🌐 Network Status"):
        st.success("✅ All systems operational")
        st.info("""
        **Active Agents:**
        - Registry Server
        - Travel Agent
        - Airline Agent
        - Restaurant Agent
        """)

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

with col1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Hi {USER_PROFILE['name']}! I'm your personal AI assistant. I can help you:\n\n✈️ **Book flights** - Try: 'Find me a flight to LAX'\n\n🍽️ **Find restaurants** - Try: 'I want Italian food tonight'\n\nWhat can I help you with?"
        }]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                intent_result = parse_intent(prompt)

                if intent_result:
                    capability, message_body = intent_result

                    if capability == "travel_booking":
                        st.markdown(f"🔍 Searching for flights to **{message_body['destination']}** on **{message_body['date']}**...")
                    else:
                        st.markdown(f"🔍 Searching for **{message_body['cuisine']}** restaurants...")

                    try:
                        result = event_loop.run_until_complete(
                            agent.execute_task(
                                capability=capability,
                                message_body=message_body
                            )
                        )

                        if capability == "travel_booking":
                            if result and result.get("status") == "options_found":
                                flights = result.get("details", [])
                                response = f"✅ Found {len(flights)} flights to {message_body['destination']}!\n\n"

                                for i, flight in enumerate(flights, 1):
                                    response += f"**{i}. {flight['flight']}** - ${flight['price']:.2f}\n"
                                    response += f"   • Departure: {flight['time']}\n"
                                    response += f"   • Seats: {flight['seats_available']} available\n\n"

                                cheapest = min(flights, key=lambda x: x['price'])
                                response += f"💰 **Best deal:** {cheapest['flight']} at ${cheapest['price']:.2f}"
                            else:
                                response = f"❌ No flights found to {message_body['destination']}. Try a different destination?"

                        elif capability == "restaurant_booking":
                            if result and result.get("status") == "success":
                                restaurants = result.get("restaurants", [])
                                response = f"✅ Found {len(restaurants)} {message_body['cuisine']} restaurants!\n\n"

                                for i, rest in enumerate(restaurants, 1):
                                    response += f"**{i}. {rest['name']}** {rest['rating']}⭐ ({rest['price']})\n"
                                    response += f"   • {rest['distance']} away\n"
                                    response += f"   • Available: {', '.join(rest['available_times'])}\n\n"

                                response += "Which one would you like? Just say the number!"
                            else:
                                response = "❌ No restaurants found. Try a different cuisine?"
                        else:
                            response = f"Got result: ```json\n{json.dumps(result, indent=2)}\n```"

                    except Exception as e:
                        response = f"❌ Oops! Something went wrong: {str(e)}"

                else:
                    response = "🤔 I'm not sure how to help with that. I can help you:\n\n✈️ Book flights (try: 'flight to SFO')\n🍽️ Find restaurants (try: 'Italian food')\n\nWhat would you like?"

                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")

with st.expander("ℹ️ How This Works"):
    st.markdown("""
    ### The Agent Web Magic ✨

    **Your assistant is powered by a decentralized network of AI agents!**

    1. **You speak naturally** - "Find me a flight to LAX"
    2. **Your assistant understands** - Parses intent (flight booking)
    3. **Discovers specialist** - Finds Travel Agent on Agent Web
    4. **Travel Agent works** - Queries Airline Agent for options
    5. **You get results** - All in seconds, automatically!

    **Key Features:**
    - 🔐 Unforgeable DID identity
    - 🤝 P2P agent collaboration
    - 💰 Economic marketplace
    - 🎯 100% reliable discovery
    - 🔒 Cryptographic security

    **This is the future of AI assistance!**
    """)

st.sidebar.title("🚀 Agent Web Demo")
st.sidebar.success(f"**Your DID:**\n`{agent.did[:30]}...`")
st.sidebar.markdown("---")
st.sidebar.info("""
**Sprint 11 Complete!**

✅ Unified conversational interface
✅ Multi-agent coordination
✅ Automatic specialist discovery
✅ Natural language understanding
✅ Profile-based personalization
""")
st.sidebar.caption("Built with Agent Web Protocol")
