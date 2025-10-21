import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent

travel_agent_sdk_instance = None

async def handle_travel_request(sender_did: str, message_body: dict):
    print(f"\n[TRAVEL AGENT] Received request from: {sender_did[:20]}...")
    task = message_body.get("task")
    destination = message_body.get("destination")
    date = message_body.get("date")

    if task == "find_flight":
        print(f"[TRAVEL AGENT] Task: Find flights to {destination} on {date}")
        if not travel_agent_sdk_instance:
            return {"status": "error", "message": "Travel Agent SDK not initialized"}

        print("[TRAVEL AGENT] Searching for 'airline_availability' capability...")

        try:
            airline_response = await travel_agent_sdk_instance.execute_task(
                capability="airline_availability",
                message_body={
                    "action": "check_flights",
                    "destination": destination,
                    "date": date
                },
                policy={'price': 0.4, 'reputation': 0.6}
            )

            print(f"[TRAVEL AGENT] Received response from Airline Agent")

            if airline_response and airline_response.get("status") == "success":
                flights = airline_response.get("flights", [])
                print(f"[TRAVEL AGENT] Forwarding {len(flights)} flight options to customer")
                return {
                    "status": "options_found",
                    "destination": destination,
                    "date": date,
                    "details": flights
                }
            else:
                return {
                    "status": "failed",
                    "reason": airline_response.get("message", "Airline agent failed")
                }
        except Exception as e:
            print(f"[TRAVEL AGENT] Error: {e}")
            return {"status": "error", "message": str(e)}

    elif task == "book_flight":
        flight_id = message_body.get("flight_id")
        print(f"[TRAVEL AGENT] Booking flight: {flight_id}")

        try:
            booking_response = await travel_agent_sdk_instance.execute_task(
                capability="airline_book_ticket",
                message_body={
                    "action": "book_ticket",
                    "flight_id": flight_id
                }
            )
            return booking_response
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "Unknown task"}

async def main():
    global travel_agent_sdk_instance

    print("=== TRAVEL AGENT (Sprint 10) ===\n")

    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="travel_agent.key",
        demo_mode=True
    )
    travel_agent_sdk_instance = agent

    agent.on_message(handle_travel_request)

    http_host = "127.0.0.1"
    http_port = 8014
    dht_host = "127.0.0.1"
    dht_port = 8484
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )
    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["travel_booking"],
        price=1.00,
        payment_method="usd"
    )

    print(f"🧳 Travel Agent DID: {agent.did}")
    print(f"📡 Listening on {http_host}:{http_port}")
    print(f"🎯 Capability: travel_booking")
    print(f"💰 Price: $1.00 per booking coordination\n")
    print("Ready to coordinate flight bookings...\n")

    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Travel Agent shutdown complete")
