# agent_web.py
import asyncio
import httpx  # NEW: Replaces 'requests'
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Callable, Dict, Any, List, Optional
import time
import json
import base64
import os

# Kademlia (DHT) import
from kademlia.network import Server as KademliaServer

# Cryptography imports (unchanged)
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

# --- SDK Models (unchanged) ---

class SignedMessage(BaseModel):
    payload: str
    signature: str

class Payload(BaseModel):
    sender_id: str
    body: Dict[str, Any]
    timestamp: float

# --- AgentRecord (for DHT) ---
class AgentRecord(BaseModel):
    # This is the data we store ON the DHT
    public_key_pem: str
    endpoint: str
    price: float
    payment_method: str

# --- ReputationStats (for client-side use) ---
class ReputationStats(BaseModel):
    successes: int = 0
    failures: int = 0
    total_response_time_ms: float = 0.0
    count: int = 0
    success_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    reputation_score: float = 5.0

# --- The Main Agent Class (v3 - Async + DHT) ---

class Agent:
    def __init__(self, agent_id: str, registry_url: str, key_file: str = "agent_key.pem",
                 default_policy: Dict[str, float] = None):
        self.agent_id = agent_id
        self.registry_url = registry_url
        self.key_file = key_file
        self.private_key, self.public_key = self._load_or_create_keys()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        if default_policy is None:
            self.default_policy = {'price': 0.6, 'reputation': 0.4}
        else:
            self.default_policy = default_policy

        self._message_handler: Callable = None

        # NEW: Async components
        self.dht_node: Optional[KademliaServer] = None
        self.http_client = httpx.AsyncClient()

    # --- 1. Key Management (unchanged) ---
    def _load_or_create_keys(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            public_key = private_key.public_key()
            print(f"Loaded existing keys for {self.agent_id}")
            return private_key, public_key
        else:
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            public_key = private_key.public_key()
            with open(self.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print(f"Generated new keys for {self.agent_id}")
            return private_key, public_key

    # --- 2. Signing & Verification (unchanged) ---
    def _sign(self, message: bytes) -> bytes:
        return self.private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

    def _verify(self, message: bytes, signature: bytes, public_key_pem: str) -> bool:
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
            public_key.verify(
                signature,
                message,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    # --- 3. NEW: DHT Methods ---

    async def start_dht_node(self, host: str, port: int, bootstrap_node: Optional[tuple] = None):
        """Initializes and runs the Kademlia DHT node."""
        self.dht_node = KademliaServer()
        await self.dht_node.listen(port, interface=host)

        if bootstrap_node:
            # Join the existing network
            await self.dht_node.bootstrap([(bootstrap_node[0], bootstrap_node[1])])
            print(f"[DHT] Node {self.agent_id} bootstrapped to {bootstrap_node}")
        else:
            print(f"[DHT] Node {self.agent_id} started as bootstrap node")

        print(f"[DHT] Node {self.agent_id} listening on {host}:{port}")

    async def publish_record(self, agent_record: AgentRecord):
        """Publishes this agent's full record to the DHT."""
        record_json = agent_record.model_dump_json()
        await self.dht_node.set(self.agent_id, record_json)
        print(f"[DHT] Published record for {self.agent_id} to the network.")

    async def fetch_record(self, agent_id: str) -> Optional[AgentRecord]:
        """Fetches an agent's record from the DHT."""
        record_json = await self.dht_node.get(agent_id)
        if record_json:
            return AgentRecord.model_validate_json(record_json)
        return None

    # --- 4. UPGRADED: Network Methods (now async) ---

    async def register(self, public_endpoint: str, capabilities: list,
                       price: float = 0.0, payment_method: str = "none"):
        """Registers agent with the network (DHT + Indexer)."""

        # Step 1: Publish full data record to the DHT
        agent_record = AgentRecord(
            public_key_pem=self.public_key_pem,
            endpoint=public_endpoint,
            price=price,
            payment_method=payment_method
        )
        await self.publish_record(agent_record)

        # Step 2: Register capabilities with the Indexer
        reg_payload = {
            "agent_id": self.agent_id,
            "capabilities": capabilities
        }
        try:
            r = await self.http_client.post(f"{self.registry_url}/register_capabilities", json=reg_payload)
            r.raise_for_status()
            print(f"[INDEXER] Successfully registered capabilities for {self.agent_id} (Price: ${price}).")
        except httpx.RequestError as e:
            print(f"ERROR: Failed to register capabilities. {e}")

    async def _discover(self, target_id: str) -> Optional[AgentRecord]:
        """Discovers another agent's info from the DHT."""
        return await self.fetch_record(target_id)

    async def _report_transaction(self, agent_id: str, success: bool, response_time_ms: float):
        """Reports the outcome of a transaction to the registry (async)."""
        report = {"agent_id": agent_id, "success": success, "response_time_ms": response_time_ms}
        try:
            await self.http_client.post(f"{self.registry_url}/report", json=report, timeout=2)
            print(f"[SDK] Reported transaction for {agent_id}. Success: {success}, Time: {response_time_ms:.1f}ms")
        except httpx.RequestError as e:
            print(f"[SDK] WARN: Failed to report transaction: {e}")

    async def send(self, target_id: str, message_body: Dict[str, Any]) -> Dict[str, Any]:
        """Sends a secure, signed P2P message (async)."""
        print(f"Sending message from {self.agent_id} to {target_id}...")

        start_time = time.perf_counter()
        success = False
        response_json = {}

        try:
            target_info = await self._discover(target_id)
            if not target_info:
                return {"error": "Failed to discover target agent from DHT"}

            payload_data = {
                "sender_id": self.agent_id,
                "body": message_body,
                "timestamp": time.time()
            }
            payload_json = json.dumps(payload_data, sort_keys=True)
            payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')

            signature = self._sign(payload_json.encode('utf-8'))
            signature_b64 = base64.b64encode(signature).decode('utf-8')

            signed_message = {"payload": payload_b64, "signature": signature_b64}

            r = await self.http_client.post(
                f"{target_info.endpoint}/invoke",
                json=signed_message,
                timeout=10
            )
            r.raise_for_status()
            response_json = r.json()
            success = True
            return response_json

        except httpx.RequestError as e:
            print(f"ERROR: Message sending failed. {e}")
            return {"error": f"Message sending failed: {e}"}

        finally:
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000.0
            await self._report_transaction(target_id, success, response_time_ms)

    # --- 5. UPGRADED: Economic Decision Engine (async) ---

    async def execute_task(self, capability: str, message_body: Dict[str, Any],
                           policy: Dict[str, float] = None) -> Dict[str, Any]:
        """Finds the BEST agent for a capability (now using DHT + Indexer) and sends it a message."""
        print(f"\n[SDK] Searching for agent with capability: '{capability}'")

        if policy is None:
            policy = self.default_policy

        # --- Step 1: Search Indexer ---
        try:
            r = await self.http_client.get(f"{self.registry_url}/search", params={"capability": capability})
            r.raise_for_status()
            agent_ids = r.json()  # List[str]
        except httpx.RequestError as e:
            return {"error": f"Failed to search for capability: {e}"}

        if not agent_ids:
            return {"error": f"No agents found with capability: {capability}"}

        print(f"[SDK] Found {len(agent_ids)} agents from indexer: {agent_ids}")

        # --- Step 2 & 3: Fetch Data (DHT) and Reputations (Indexer) in Parallel ---
        try:
            # Fetch all agent records from DHT
            record_tasks = [self._discover(agent_id) for agent_id in agent_ids]

            # Fetch all reputations from Indexer
            rep_task = self.http_client.post(f"{self.registry_url}/get_reputations",
                                             json={"agent_ids": agent_ids})

            # Run all lookups concurrently
            results = await asyncio.gather(*record_tasks, rep_task)

            records = results[:-1]  # List[AgentRecord or None]
            rep_response = results[-1].json()  # Dict response from API

            # Parse reputation data
            reputations = {}
            for agent_id, stats_dict in rep_response['reputations'].items():
                reputations[agent_id] = ReputationStats(**stats_dict)

        except (httpx.RequestError, json.JSONDecodeError) as e:
            return {"error": f"Failed during data/reputation fetching: {e}"}

        # --- Step 4: Rank Candidates ---
        candidates_data = []
        for i, record in enumerate(records):
            if record:  # Check if DHT lookup was successful
                agent_id = agent_ids[i]
                candidates_data.append({
                    "id": agent_id,
                    "price": record.price,
                    "reputation": reputations[agent_id].reputation_score
                })
                print(f"[SDK] Fetched from DHT: {agent_id} - Price: ${record.price}, Rep: {reputations[agent_id].reputation_score:.2f}")

        if not candidates_data:
            return {"error": "Found agent IDs but failed to fetch any records from DHT."}

        if len(candidates_data) == 1:
            winner_id = candidates_data[0]['id']
            print(f"[SDK] Only one candidate found: {winner_id}")
        else:
            print(f"\n[SDK] Ranking {len(candidates_data)} candidates by policy: Price={policy.get('price', 0.5)*100:.0f}%, Reputation={policy.get('reputation', 0.5)*100:.0f}%")

            # Normalize Price (lower is better)
            prices = [c['price'] for c in candidates_data]
            min_price = min(prices)
            max_price = max(prices)

            # Normalize Reputation (higher is better)
            reps = [c['reputation'] for c in candidates_data]
            min_rep = min(reps)
            max_rep = max(reps)

            scored_candidates = []
            for c in candidates_data:
                # Price scoring (inverted - lower is better)
                if max_price == min_price:
                    price_score = 1.0
                else:
                    price_score = 1.0 - ((c['price'] - min_price) / (max_price - min_price))

                # Reputation scoring (higher is better)
                if max_rep == min_rep:
                    rep_score = 1.0
                else:
                    rep_score = (c['reputation'] - min_rep) / (max_rep - min_rep)

                # Calculate utility
                utility_score = (price_score * policy.get('price', 0.5)) + \
                                (rep_score * policy.get('reputation', 0.5))

                scored_candidates.append((utility_score, c))
                print(f"  - {c['id']}: Price=${c['price']:.2f}, Rep={c['reputation']:.2f}, Utility={utility_score:.3f}")

            # Sort by highest utility
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            winner_id = scored_candidates[0][1]['id']

        print(f"\n[SDK] Winner selected: {winner_id}")

        # --- Step 5: Send message to winner ---
        return await self.send(target_id=winner_id, message_body=message_body)

    # --- 6. UPGRADED: Listener (async, no threading) ---

    def on_message(self, func: Callable):
        """Decorator to register the user's message handler."""
        self._message_handler = func
        return func

    def _create_listener_app(self):
        """Creates the internal FastAPI app for this agent."""
        app = FastAPI(title=f"Agent Listener: {self.agent_id}")

        @app.post("/invoke")
        async def handle_invoke(message: SignedMessage, request: Request):
            if not self._message_handler:
                raise HTTPException(status_code=500, detail="Agent has no message handler")

            try:
                payload_json = base64.b64decode(message.payload).decode('utf-8')
                signature = base64.b64decode(message.signature)
                payload: Dict = json.loads(payload_json)
                sender_id = payload['sender_id']
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid message format: {e}")

            # Discover sender from DHT to get their public key
            sender_record = await self.fetch_record(sender_id)
            if not sender_record:
                raise HTTPException(status_code=403, detail="Could not discover sender identity from DHT")

            is_valid = self._verify(
                payload_json.encode('utf-8'),
                signature,
                sender_record.public_key_pem
            )

            if not is_valid:
                raise HTTPException(status_code=403, detail="Invalid signature")

            print(f"Received valid message from {sender_id}")
            # Call the user's handler (assuming it's synchronous for now)
            response_body = self._message_handler(sender_id, payload['body'])
            return response_body

        return app

    async def listen_and_join(self, http_host: str, http_port: int,
                              dht_host: str, dht_port: int,
                              bootstrap_node: Optional[tuple] = None):
        """
        Runs all agent services (DHT node + FastAPI server) in the same event loop.
        This is the new main entry point for a running agent.
        """
        # 1. Start the DHT node
        await self.start_dht_node(dht_host, dht_port, bootstrap_node)

        # 2. Configure and start the FastAPI (listener) server
        app = self._create_listener_app()
        config = uvicorn.Config(app, host=http_host, port=http_port, log_level="info")
        server = uvicorn.Server(config)

        print(f"\n--- Agent {self.agent_id} is LIVE ---")
        print(f"--- HTTP listener on {http_host}:{http_port} ---")
        print(f"--- DHT node on {dht_host}:{dht_port} ---\n")

        # 3. Run the server
        await server.serve()