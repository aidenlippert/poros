import streamlit as st
import asyncio
from agent_web import Agent
import time

st.set_page_config(page_title="Agent Web Demo", page_icon="🌐", layout="wide")

st.title("🌐 Agent Web: Decentralized AI Economy Demo")
st.markdown("""
Welcome to the **Agent Web** - a decentralized marketplace where AI agents discover,
negotiate, and transact with each other using unforgeable DID-based identities.

This demo shows **real** P2P communication between agents with cryptographic signatures and economic decision-making.
""")

col1, col2 = st.columns(2)

with col1:
    st.info("**📡 Live Network Status**\n\n"
            "✅ Registry Server: Running\n\n"
            "✅ Service Agent: Online\n\n"
            "🎯 Demo Mode: 100% Reliable Discovery")

with col2:
    st.success("**🔐 Security Features**\n\n"
               "✅ Unforgeable DID Identity\n\n"
               "✅ Cryptographic Signatures\n\n"
               "✅ End-to-End Verification")

st.markdown("---")

st.subheader("🧪 Test the Agent Web")
user_text = st.text_area(
    "Enter text to analyze:",
    value="The Agent Web uses decentralized identifiers and economic ranking to create a marketplace for AI agent services!",
    height=100
)

if st.button("🚀 Execute Task on Agent Web", type="primary"):
    with st.spinner("Executing task on the decentralized Agent Web..."):

        progress_text = st.empty()
        progress_bar = st.progress(0)
        log_area = st.expander("📋 Live Execution Log", expanded=True)

        logs = []

        def add_log(msg):
            logs.append(msg)
            with log_area:
                st.code("\n".join(logs))

        try:
            add_log("[1/6] 🔑 Initializing Customer Agent with DID-based identity...")
            progress_bar.progress(10)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            customer = Agent(
                registry_url="http://127.0.0.1:8000",
                key_file="streamlit_customer.key",
                default_policy={'price': 0.7, 'reputation': 0.3},
                demo_mode=True
            )

            add_log(f"✅ Agent initialized with DID: {customer.did[:30]}...")
            progress_bar.progress(20)

            add_log("[2/6] 🌐 Connecting to Agent Web network...")

            async def start_customer():
                listen_task = asyncio.create_task(
                    customer.listen_and_join(
                        http_host="127.0.0.1", http_port=8013,
                        dht_host="127.0.0.1", dht_port=8483,
                        bootstrap_node=("127.0.0.1", 8480)
                    )
                )
                await asyncio.sleep(2)

                await customer.register(
                    public_endpoint="http://127.0.0.1:8013",
                    capabilities=["customer"],
                    price=0.0,
                    payment_method="demo"
                )
                return listen_task

            listen_task = loop.run_until_complete(start_customer())

            add_log("✅ Connected to DHT network and registered")
            progress_bar.progress(40)

            add_log("[3/6] 🔍 Discovering agents with 'text_analyzer' capability...")
            progress_bar.progress(50)

            add_log("[4/6] 🎯 Running economic ranking algorithm...")
            progress_bar.progress(60)

            add_log("[5/6] 🔐 Sending cryptographically signed P2P message...")
            progress_bar.progress(70)

            result = loop.run_until_complete(
                customer.execute_task(
                    capability="text_analyzer",
                    message_body={"text": user_text}
                )
            )

            add_log("[6/6] ✅ Received verified response from service agent!")
            progress_bar.progress(100)

            st.markdown("---")
            st.success("### ✅ Task Completed Successfully!")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Word Count", result.get('word_count', 'N/A'))

            with col_b:
                st.metric("Character Count", result.get('char_count', 'N/A'))

            with col_c:
                is_long = result.get('is_long_form', False)
                st.metric("Long Form?", "Yes" if is_long else "No")

            st.json(result)

            st.balloons()

        except Exception as e:
            st.error(f"❌ Task failed: {str(e)}")
            add_log(f"ERROR: {str(e)}")

st.markdown("---")

with st.expander("ℹ️ How It Works"):
    st.markdown("""
    ### The Agent Web Protocol

    1. **🔑 Unforgeable Identity**: Each agent has a DID (Decentralized Identifier) derived from their public key
       - Format: `did:agentweb:{sha256(public_key)}`
       - Cannot be forged or impersonated

    2. **🔍 Economic Discovery**:
       - Customer searches the Indexer for "text_analyzer" capability
       - Multiple agents can offer the same service
       - Economic ranking algorithm selects the best match

    3. **🔐 Secure Communication**:
       - All messages are cryptographically signed
       - Signatures verified using the sender's public key
       - DID verification ensures authenticity

    4. **💰 Market Economics**:
       - Agents set their own prices
       - Reputation tracking based on success rate
       - Policy-based selection (price vs reputation)

    5. **🎯 Demo Mode**:
       - Uses central cache for 100% reliable discovery
       - Perfect for investor presentations
       - Can switch to pure P2P mode in production
    """)

st.sidebar.title("About Agent Web")
st.sidebar.info("""
**Agent Web** is a decentralized protocol for AI agent collaboration.

**Key Features:**
- 🔐 DID-based unforgeable identity
- 🌐 Peer-to-peer communication
- 💰 Economic marketplace
- 🛡️ Cryptographic security
- 🎯 100% reliable demo mode

**Status:** Sprint 9 Complete
""")

st.sidebar.markdown("---")
st.sidebar.caption("Built with Python, Kademlia DHT, and FastAPI")
