import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import random

SIMULATED_FLIGHTS = {
    "SFO": [
        {"flight": "UA123", "time": "9:00 AM", "price": 250.00, "seats_available": 5},
        {"flight": "UA456", "time": "2:00 PM", "price": 220.00, "seats_available": 10},
        {"flight": "AA789", "time": "10:30 AM", "price": 265.00, "seats_available": 3},
    ],
    "LAX": [
        {"flight": "UA777", "time": "11:00 AM", "price": 180.00, "seats_available": 8},
        {"flight": "DL888", "time": "4:00 PM", "price": 195.00, "seats_available": 12},
    ]
}

def handle_airline_request(sender_did: str, message_body: dict):
    print(f"\n[AIRLINE AGENT] Received request from: {sender_did[:20]}...")
    action = message_body.get("action")
    destination = message_body.get("destination")
    date = message_body.get("date")

    if action == "check_flights":
        flights = SIMULATED_FLIGHTS.get(destination, [])
        print(f"[AIRLINE AGENT] Found {len(flights)} flights for {destination}")
        return {"status": "success", "flights": flights}

    elif action == "book_ticket":
        flight_id = message_body.get("flight_id")
        print(f"[AIRLINE AGENT] Attempting to book {flight_id}...")
        if random.random() > 0.1:
            confirmation_id = f"CONF-{random.randint(10000, 99999)}"
            print(f"[AIRLINE AGENT] Booking successful: {confirmation_id}")
            return {"status": "success", "confirmation_id": confirmation_id, "flight": flight_id}
        else:
            print(f"[AIRLINE AGENT] Booking failed for {flight_id}")
            return {"status": "failed", "reason": "Seats no longer available"}
    else:
        return {"status": "error", "message": "Unknown action"}

async def main():
    print("=== AIRLINE AGENT (Sprint 10) ===\n")

    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="airline_agent.key",
        demo_mode=True
    )

    agent.on_message(handle_airline_request)

    http_host = "127.0.0.1"
    http_port = 8015
    dht_host = "127.0.0.1"
    dht_port = 8485
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )
    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["airline_availability", "airline_book_ticket"],
        price=0.10,
        payment_method="points"
    )

    print(f"✈️  Airline Agent DID: {agent.did}")
    print(f"📡 Listening on {http_host}:{http_port}")
    print(f"🎯 Capabilities: airline_availability, airline_book_ticket")
    print(f"💰 Price: $0.10 per query\n")
    print("Waiting for travel agent requests...\n")

    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Airline Agent shutdown complete")
