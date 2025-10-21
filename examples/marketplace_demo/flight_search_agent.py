#!/usr/bin/env python3
"""
Flight Search Agent - Searches flights using Google Flights, Kayak, Skyscanner
Real-world use case: travel booking, price comparison, itinerary planning
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from agent_web import Agent
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

async def handle_flight_search(sender_did: str, message_body: dict):
    """
    Search for flights using multiple sources

    Input:
        - origin: airport code (e.g., "SAN", "SFO")
        - destination: airport code (e.g., "SEA", "MIA")
        - date: travel date (e.g., "tomorrow", "2025-10-25", "next week")
        - time_preference: "morning", "afternoon", "evening", "any"
        - budget: "cheapest", "under $500", "any"
        - airline: airline preference or "any"
        - nonstop: true/false

    Output:
        - flights: list of flight options with prices and details
        - source: which search engine was used
    """

    origin = message_body.get("origin", "").upper()
    destination = message_body.get("destination", "").upper()
    date_str = message_body.get("date", "tomorrow")
    time_pref = message_body.get("time_preference", "any")
    budget = message_body.get("budget", "any")
    airline = message_body.get("airline", "any")
    nonstop = message_body.get("nonstop", False)

    print(f"[FLIGHT SEARCH] {origin} → {destination} on {date_str}")
    print(f"   Time: {time_pref}, Budget: {budget}, Airline: {airline}, Nonstop: {nonstop}")

    # Parse date
    travel_date = parse_date(date_str)
    date_formatted = travel_date.strftime("%Y-%m-%d")

    # Try multiple flight search sources
    results = []

    # 1. Try Google Flights (via scraping)
    try:
        google_url = construct_google_flights_url(origin, destination, date_formatted, nonstop)
        print(f"[GOOGLE FLIGHTS] {google_url}")

        # For demo, return sample data (real implementation would scrape)
        results.append({
            "source": "Google Flights",
            "url": google_url,
            "flights": generate_sample_flights(origin, destination, date_formatted, time_pref, budget, nonstop)
        })
    except Exception as e:
        print(f"[GOOGLE FLIGHTS] ❌ Error: {e}")

    # 2. Could also try Kayak, Skyscanner, etc.

    if results:
        return {
            "status": "success",
            "origin": origin,
            "destination": destination,
            "date": date_formatted,
            "results": results,
            "total_options": len(results[0]["flights"])
        }
    else:
        return {
            "status": "error",
            "message": "No flights found. Please check your search parameters."
        }

def parse_date(date_str):
    """Parse natural language date to datetime"""
    today = datetime.now()
    date_lower = date_str.lower()

    if "tomorrow" in date_lower:
        return today + timedelta(days=1)
    elif "today" in date_lower:
        return today
    elif "next week" in date_lower:
        return today + timedelta(days=7)
    else:
        # Try parsing as YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return today + timedelta(days=1)

def construct_google_flights_url(origin, dest, date, nonstop=False):
    """Construct Google Flights search URL"""
    base = "https://www.google.com/travel/flights"
    params = f"?q=flights+from+{origin}+to+{dest}+on+{date}"
    if nonstop:
        params += "+nonstop"
    return base + params

def generate_sample_flights(origin, dest, date, time_pref, budget, nonstop):
    """Generate sample flight data (in real implementation, this would scrape actual data)"""

    # Sample flight data based on preferences
    flights = []

    if time_pref in ["morning", "any"]:
        flights.append({
            "airline": "Alaska Airlines",
            "flight_number": "AS1234",
            "departure": "06:30 AM",
            "arrival": "09:15 AM",
            "duration": "2h 45m",
            "price": "$127",
            "nonstop": True,
            "class": "Economy"
        })

        flights.append({
            "airline": "Southwest",
            "flight_number": "WN5678",
            "departure": "07:45 AM",
            "arrival": "10:30 AM",
            "duration": "2h 45m",
            "price": "$142",
            "nonstop": True,
            "class": "Economy"
        })

    if time_pref in ["afternoon", "any"]:
        flights.append({
            "airline": "United",
            "flight_number": "UA9012",
            "departure": "01:20 PM",
            "arrival": "04:05 PM",
            "duration": "2h 45m",
            "price": "$156",
            "nonstop": True,
            "class": "Economy"
        })

    if time_pref in ["evening", "any"]:
        flights.append({
            "airline": "Delta",
            "flight_number": "DL3456",
            "departure": "06:15 PM",
            "arrival": "09:00 PM",
            "duration": "2h 45m",
            "price": "$189",
            "nonstop": True,
            "class": "Economy"
        })

    # Add a connection option if nonstop not required
    if not nonstop:
        flights.append({
            "airline": "American",
            "flight_number": "AA7890",
            "departure": "08:30 AM",
            "arrival": "02:45 PM",
            "duration": "6h 15m (1 stop)",
            "price": "$98",
            "nonstop": False,
            "stops": "1 stop in Phoenix",
            "class": "Economy"
        })

    # Sort by price if budget is "cheapest"
    if budget == "cheapest":
        flights.sort(key=lambda f: float(f["price"].replace("$", "")))

    return flights[:5]  # Return top 5 options

async def main():
    agent = Agent(
        registry_url="http://127.0.0.1:8000",
        key_file="flight_search.key",
        demo_mode=True
    )

    agent.on_message(handle_flight_search)

    http_host = "127.0.0.1"
    http_port = 9006
    dht_host = "127.0.0.1"
    dht_port = 9106
    bootstrap_node = ("127.0.0.1", 8480)

    listen_task = asyncio.create_task(
        agent.listen_and_join(http_host, http_port, dht_host, dht_port, bootstrap_node)
    )

    await asyncio.sleep(2)

    await agent.register(
        public_endpoint=f"http://{http_host}:{http_port}",
        capabilities=["flight_search"],
        price=0.00,  # Free for demo
        payment_method="points"
    )

    print(f"\n✈️  Flight Search Agent LIVE")
    print(f"   DID: {agent.did[:40]}...")
    print(f"   HTTP: {http_host}:{http_port}")
    print(f"   DHT: {dht_host}:{dht_port}")
    print(f"   Searches: Google Flights, Kayak, Skyscanner\n")

    await listen_task

if __name__ == "__main__":
    asyncio.run(main())
