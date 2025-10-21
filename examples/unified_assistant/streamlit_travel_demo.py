import streamlit as st
import asyncio
import time
from agent_web import Agent

st.set_page_config(page_title="Agent Web Travel Demo", page_icon="✈️", layout="wide")

if 'agent' not in st.session_state:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    quality_policy = {'price': 0.2, 'reputation': 0.8}
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="personal_assistant.key",
        default_policy=quality_policy,
        demo_mode=True
    )

    async def start_agent():
        listen_task = asyncio.create_task(
            agent.listen_and_join(
                http_host="127.0.0.1", http_port=8016,
                dht_host="127.0.0.1", dht_port=8486,
                bootstrap_node=("127.0.0.1", 8480)
            )
        )
        await asyncio.sleep(2)

        await agent.register(
            public_endpoint="http://127.0.0.1:8016",
            capabilities=["personal_assistant_ui"],
            price=0.0,
            payment_method="free"
        )
        return listen_task

    st.session_state.listen_task = loop.run_until_complete(start_agent())
    st.session_state.agent = agent
    st.session_state.loop = loop

customer_agent = st.session_state.agent
event_loop = st.session_state.loop

st.title("✈️ Agent Web Travel Booking Demo")
st.markdown("""
**Multi-Agent Coordination in Action!**

Your Personal Assistant → Travel Agent → Airline Agent

Watch agents collaborate to find you the best flights!
""")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Flight Search")

    destination = st.selectbox(
        "Destination Airport",
        ["SFO", "LAX", "NYC"],
        help="SFO and LAX have flights. NYC will intentionally fail (no routes)."
    )

    day = st.selectbox(
        "Travel Day",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )

    if st.button("🚀 Find Flights", type="primary"):
        with st.spinner("Your Personal Agent is coordinating with the Travel Agent..."):

            log_container = st.expander("📋 Live Agent Communication Log", expanded=True)
            log_messages = []

            def add_log(msg):
                log_messages.append(msg)
                with log_container:
                    st.code("\n".join(log_messages))
                time.sleep(0.3)

            add_log(f"[1/5] 🤖 Personal Agent: Received your request for {destination} on {day}")
            add_log("[2/5] 🔍 Personal Agent: Searching for 'travel_booking' capability...")
            add_log("[3/5] 🧳 Found Travel Agent! Sending request...")

            try:
                response = event_loop.run_until_complete(
                    customer_agent.execute_task(
                        capability="travel_booking",
                        message_body={
                            "task": "find_flight",
                            "destination": destination,
                            "date": day
                        }
                    )
                )

                add_log("[4/5] ✈️  Travel Agent queried Airline Agent...")
                add_log("[5/5] ✅ Personal Agent: Received final response!")

                st.markdown("---")
                st.subheader("📊 Flight Results")

                if response and response.get("status") == "options_found":
                    st.success(f"✅ Found flights to {destination}!")

                    flights = response.get("details", [])
                    if flights:
                        st.dataframe(
                            flights,
                            column_config={
                                "flight": "Flight Number",
                                "time": "Departure Time",
                                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                                "seats_available": "Seats Available"
                            },
                            hide_index=True,
                            use_container_width=True
                        )

                        cheapest = min(flights, key=lambda x: x['price'])
                        st.info(f"💰 Best Deal: {cheapest['flight']} at ${cheapest['price']:.2f}")
                    else:
                        st.warning("No flights found for this destination.")

                elif response and response.get("status") == "failed":
                    st.error(f"❌ Search failed: {response.get('reason', 'Unknown error')}")
                    st.json(response)
                else:
                    st.error("❌ Unexpected response from agent network")
                    st.json(response)

            except Exception as e:
                add_log(f"[ERROR] {str(e)}")
                st.error(f"❌ Task failed: {str(e)}")

with col2:
    st.subheader("🌐 Network Status")

    st.info("""
    **Active Agents:**
    - 🏛️ Registry Server (port 8000)
    - 🧳 Travel Agent (port 8014)
    - ✈️  Airline Agent (port 8015)
    - 🤖 Your Personal Agent (port 8016)
    """)

    st.success("✅ All systems operational")

    st.markdown("---")
    st.subheader("🔐 Your Identity")
    st.code(customer_agent.did[:40] + "...", language="text")

st.sidebar.title("ℹ️ How It Works")
st.sidebar.markdown("""
### Multi-Agent Architecture

1. **Personal Agent** (You)
   - Understands your request
   - Finds the right specialist

2. **Travel Agent** (Broker)
   - Coordinates with airlines
   - Compares options
   - Negotiates on your behalf

3. **Airline Agent** (Service)
   - Provides real flight data
   - Handles bookings
   - Manages inventory

### Key Features
- 🔐 Unforgeable DID identity
- 🤝 P2P agent communication
- 💰 Economic marketplace
- 🎯 100% reliable discovery
- 🔒 Cryptographic signatures
""")

st.sidebar.markdown("---")
st.sidebar.caption("**Sprint 10:** Multi-Agent Travel Demo")
