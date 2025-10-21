import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
import random

SIMULATED_RESTAURANTS = {
    "italian": [
        {"name": "Mama's Trattoria", "price": "$$", "rating": 4.8, "available_times": ["6:00 PM", "8:00 PM"], "distance": "0.5 miles"},
        {"name": "Luigi's", "price": "$$$", "rating": 4.5, "available_times": ["7:00 PM", "9:00 PM"], "distance": "1.2 miles"},
    ],
    "mexican": [
        {"name": "El Taco Loco", "price": "$", "rating": 4.6, "available_times": ["6:30 PM", "8:30 PM"], "distance": "0.8 miles"},
        {"name": "Casa Mexicana", "price": "$$", "rating": 4.7, "available_times": ["7:00 PM"], "distance": "2.1 miles"},
    ],
    "japanese": [
        {"name": "Sakura Sushi", "price": "$$$", "rating": 4.9, "available_times": ["6:00 PM", "8:00 PM"], "distance": "1.5 miles"},
        {"name": "Tokyo Express", "price": "$$", "rating": 4.4, "available_times": ["7:30 PM"], "distance": "0.9 miles"},
    ]
}

def handle_restaurant_request(sender_did: str, message_body: dict):
    print(f"\n[RESTAURANT AGENT] Request from {sender_did[:20]}...")
    action = message_body.get("action")

    if action == "search":
        cuisine = message_body.get("cuisine", "").lower()
        price_pref = message_body.get("price_preference")
        party_size = message_body.get("party_size", 2)

        restaurants = SIMULATED_RESTAURANTS.get(cuisine, [])

        if price_pref:
            restaurants = [r for r in restaurants if r["price"] == price_pref]

        print(f"[RESTAURANT AGENT] Found {len(restaurants)} {cuisine} restaurants")
        return {"status": "success", "restaurants": restaurants, "cuisine": cuisine}

    elif action == "book":
        restaurant_name = message_body.get("restaurant_name")
        time = message_body.get("time")
        party_size = message_body.get("party_size")
        special_requests = message_body.get("special_requests", "")

        print(f"[RESTAURANT AGENT] Booking {restaurant_name} for {party_size} at {time}")

        if random.random() > 0.1:
            confirmation = f"CONF-{random.randint(1000, 9999)}"
            print(f"[RESTAURANT AGENT] Booking confirmed: {confirmation}")
            return {
                "status": "confirmed",
                "confirmation_number": confirmation,
                "restaurant": restaurant_name,
                "time": time,
                "party_size": party_size,
                "special_requests": special_requests
            }
        else:
            return {"status": "failed", "reason": "Restaurant fully booked"}

    return {"status": "error", "message": "Unknown action"}

async def main():
    print("=== RESTAURANT AGENT (Sprint 10) ===\n")

    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="restaurant_agent.key",
        demo_mode=True
    )

    agent.on_message(handle_restaurant_request)

    listen_task = asyncio.create_task(
        agent.listen_and_join(
            http_host="127.0.0.1", http_port=8017,
            dht_host="127.0.0.1", dht_port=8487,
            bootstrap_node=("127.0.0.1", 8480)
        )
    )
    await asyncio.sleep(2)

    await agent.register(
        public_endpoint="http://127.0.0.1:8017",
        capabilities=["restaurant_booking"],
        price=0.50,
        payment_method="commission"
    )

    print(f"🍽️  Restaurant Agent DID: {agent.did}")
    print(f"📡 Listening on 127.0.0.1:8017")
    print(f"🎯 Capability: restaurant_booking")
    print("Waiting for reservation requests...\n")

    await listen_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Restaurant Agent shutdown")
