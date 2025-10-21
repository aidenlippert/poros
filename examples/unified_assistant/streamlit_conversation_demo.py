import streamlit as st
import asyncio
from agent_web import Agent
import json

st.set_page_config(page_title="Your Personal AI Assistant", page_icon="🤖", layout="wide")

USER_PROFILE = {
    "name": "Alex Johnson",
    "location": "San Francisco, CA",
    "dietary_restrictions": ["vegetarian"],
    "preferred_price": "$$",
    "payment_method": "Visa •••• 4242",
    "default_party_size": 2
}

if 'agent' not in st.session_state:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="personal_ai_assistant.key",
        default_policy={'price': 0.3, 'reputation': 0.7},
        demo_mode=True
    )

    async def start_agent():
        listen_task = asyncio.create_task(
            agent.listen_and_join(
                http_host="127.0.0.1", http_port=8018,
                dht_host="127.0.0.1", dht_port=8488,
                bootstrap_node=("127.0.0.1", 8480)
            )
        )
        await asyncio.sleep(2)

        await agent.register(
            public_endpoint="http://127.0.0.1:8018",
            capabilities=["personal_assistant"],
            price=0.0,
            payment_method="free"
        )
        return listen_task

    st.session_state.listen_task = loop.run_until_complete(start_agent())
    st.session_state.agent = agent
    st.session_state.loop = loop
    st.session_state.conversation = []
    st.session_state.booking_context = {}

agent = st.session_state.agent
loop = st.session_state.loop

st.title("🤖 Your Personal AI Assistant")
st.caption(f"Powered by Agent Web • DID: `{agent.did[:20]}...`")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Conversation")

    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.conversation:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

    user_input = st.chat_input("Ask your assistant anything...")

    if user_input:
        st.session_state.conversation.append({"role": "user", "content": user_input})

        with st.spinner("🤔 Your assistant is thinking..."):
            user_lower = user_input.lower()

            if any(word in user_lower for word in ["dinner", "restaurant", "eat", "reservation"]):
                if "italian" in user_lower:
                    cuisine = "italian"
                elif "mexican" in user_lower:
                    cuisine = "mexican"
                elif "japanese" in user_lower or "sushi" in user_lower:
                    cuisine = "japanese"
                else:
                    response = "I'd love to help you find a restaurant! What type of cuisine are you in the mood for? I can search for Italian, Mexican, or Japanese."
                    st.session_state.conversation.append({"role": "assistant", "content": response})
                    st.rerun()

                try:
                    result = loop.run_until_complete(
                        agent.execute_task(
                            capability="restaurant_booking",
                            message_body={
                                "action": "search",
                                "cuisine": cuisine,
                                "price_preference": USER_PROFILE["preferred_price"],
                                "party_size": USER_PROFILE["default_party_size"]
                            }
                        )
                    )

                    if result and result.get("status") == "success":
                        restaurants = result.get("restaurants", [])

                        if restaurants:
                            response = f"Great! I found {len(restaurants)} {cuisine} restaurants near you:\n\n"
                            for i, rest in enumerate(restaurants, 1):
                                response += f"**{i}. {rest['name']}** - {rest['rating']}⭐ ({rest['price']})\n"
                                response += f"   • {rest['distance']} away\n"
                                response += f"   • Available: {', '.join(rest['available_times'])}\n\n"

                            response += "Which one would you like to book? Just say the number!"
                            st.session_state.booking_context = {"restaurants": restaurants, "cuisine": cuisine}
                        else:
                            response = f"I couldn't find any {cuisine} restaurants matching your preferences. Would you like to try a different cuisine?"
                    else:
                        response = "I'm having trouble connecting to restaurant services right now. Can you try again?"

                    st.session_state.conversation.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.session_state.conversation.append({"role": "assistant", "content": f"Oops! Something went wrong: {str(e)}"})

            elif any(word in user_lower for word in ["1", "2", "first", "second", "book"]) and st.session_state.booking_context:
                try:
                    choice = 0 if "1" in user_lower or "first" in user_lower else 1
                    restaurants = st.session_state.booking_context.get("restaurants", [])

                    if choice < len(restaurants):
                        selected = restaurants[choice]
                        time = selected["available_times"][0]

                        result = loop.run_until_complete(
                            agent.execute_task(
                                capability="restaurant_booking",
                                message_body={
                                    "action": "book",
                                    "restaurant_name": selected["name"],
                                    "time": time,
                                    "party_size": USER_PROFILE["default_party_size"],
                                    "special_requests": "Vegetarian options please"
                                }
                            )
                        )

                        if result and result.get("status") == "confirmed":
                            response = f"✅ **Reservation Confirmed!**\n\n"
                            response += f"📍 {selected['name']}\n"
                            response += f"🕐 {time}\n"
                            response += f"👥 Party of {USER_PROFILE['default_party_size']}\n"
                            response += f"🎫 Confirmation: {result['confirmation_number']}\n\n"
                            response += f"💳 I'll charge your {USER_PROFILE['payment_method']} when you arrive.\n\n"
                            response += "Enjoy your dinner! 🍽️"

                            st.session_state.booking_context = {}
                        else:
                            response = "Sorry, that restaurant is fully booked. Would you like to try another one?"

                        st.session_state.conversation.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.session_state.conversation.append({"role": "assistant", "content": f"Booking failed: {str(e)}"})

            else:
                responses = [
                    "I'm your personal AI assistant! I can help you book restaurants. Just say something like 'Find me an Italian restaurant for dinner!'",
                    "I'd be happy to help! I specialize in finding and booking restaurants. What are you in the mood for?",
                    f"Hi {USER_PROFILE['name']}! I can make dinner reservations for you. What sounds good tonight?"
                ]
                import random
                response = random.choice(responses)
                st.session_state.conversation.append({"role": "assistant", "content": response})

        st.rerun()

with col2:
    st.subheader("👤 Your Profile")
    st.info(f"""
    **Name:** {USER_PROFILE['name']}
    **Location:** {USER_PROFILE['location']}
    **Dietary:** {', '.join(USER_PROFILE['dietary_restrictions'])}
    **Price Preference:** {USER_PROFILE['preferred_price']}
    **Payment:** {USER_PROFILE['payment_method']}
    **Default Party Size:** {USER_PROFILE['default_party_size']}
    """)

    st.markdown("---")

    st.subheader("🤖 How It Works")
    st.success("""
    **Your assistant:**
    1. Understands natural language
    2. Uses YOUR profile automatically
    3. Finds best options for YOU
    4. Books with ONE click
    5. Charges YOUR saved payment

    **All without you lifting a finger!**
    """)

    if st.button("🔄 Reset Conversation"):
        st.session_state.conversation = []
        st.session_state.booking_context = {}
        st.rerun()

st.markdown("---")
st.caption("**Sprint 10:** Conversational AI Assistant Demo - This is what the future looks like!")
