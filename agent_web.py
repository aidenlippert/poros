# agent_web.py - DID-Enabled Agent Web SDK (v4)
import asyncio
import httpx
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Callable, Dict, Any, List, Optional
import time
import json
import base64
import os
import hashlib  # NEW: For DID generation

# Kademlia (DHT) import
from kademlia.network import Server as KademliaServer

# Cryptography imports
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

# --- SDK Models ---

class SignedMessage(BaseModel):
    payload: str
    signature: str

class Payload(BaseModel):
    sender_did: str  # RENAMED from sender_id
    body: Dict[str, Any]
    timestamp: float

class AgentRecord(BaseModel):
    # This now contains the pubkey so we can verify the DID
    public_key_pem: str
    endpoint: str
    price: float
    payment_method: str

class ReputationStats(BaseModel):
    successes: int = 0
    failures: int = 0
    total_response_time_ms: float = 0.0
    count: int = 0
    success_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    reputation_score: float = 5.0

# --- The Main Agent Class (v4 - DID Enabled) ---

class Agent:
    def __init__(self, registry_url: str, key_file: str,
                 default_policy: Dict[str, float] = None, demo_mode: bool = False):
        # 'agent_id' is GONE.
        self.registry_url = registry_url
        self.key_file = key_file
        self.demo_mode = demo_mode  # SPRINT 9: Enable hybrid demo mode
        self.private_key, self.public_key = self._load_or_create_keys()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        # NEW: Generate unforgeable Decentralized Identifier
        self.did = self._create_did_from_key()
        print(f"Agent initialized. Key: {self.key_file}, DID: {self.did}")

        if default_policy is None:
            self.default_policy = {'price': 0.6, 'reputation': 0.4}
        else:
            self.default_policy = default_policy

        self._message_handler: Callable = None

        self.dht_node: Optional[KademliaServer] = None
        self.http_client = httpx.AsyncClient()

    # --- 1. Key & DID Management ---

    def _load_or_create_keys(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            public_key = private_key.public_key()
            print(f"Loaded existing keys for {self.key_file}")
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
            print(f"Generated new keys for {self.key_file}")
            return private_key, public_key

    def _create_did_from_key(self) -> str:
        """Creates a verifiable DID from the agent's public key."""
        # did:method:method-specific-identifier
        # Our method is 'agentweb'
        # Our identifier is the sha256 hash of the PEM
        digest = hashlib.sha256(self.public_key_pem.encode('utf-8')).hexdigest()
        return f"did:agentweb:{digest}"

    def _verify_did(self, did: str, public_key_pem: str) -> bool:
        """Verifies that a DID correctly matches a public key."""
        try:
            digest = hashlib.sha256(public_key_pem.encode('utf-8')).hexdigest()
            expected_did = f"did:agentweb:{digest}"
            return did == expected_did
        except Exception:
            return False

    # --- 2. Signing & Verification ---

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

    # --- 3. DHT Methods ---

    async def start_dht_node(self, host: str, port: int, bootstrap_node: Optional[tuple] = None):
        """Initializes and runs the Kademlia DHT node."""
        self.dht_node = KademliaServer()
        await self.dht_node.listen(port, interface=host)

        if bootstrap_node:
            # Join the existing network
            await self.dht_node.bootstrap([(bootstrap_node[0], bootstrap_node[1])])
            print(f"[DHT] Node {self.did} bootstrapped to {bootstrap_node}")
        else:
            print(f"[DHT] Node {self.did} started as bootstrap node")

        print(f"[DHT] Node {self.did} listening on {host}:{port}")

    async def publish_record(self, agent_record: AgentRecord):
        """Publishes this agent's full record to the DHT under its DID."""
        record_json = agent_record.model_dump_json()
        # Publish to DHT using our DID as the key
        await self.dht_node.set(self.did, record_json)
        print(f"[DHT] Published record for {self.did} to the network.")

    async def fetch_record(self, did: str) -> Optional[AgentRecord]:
        """Fetches and *verifies* an agent's record from the DHT."""
        record_json = await self.dht_node.get(did)
        if not record_json:
            print(f"[SDK] DHT lookup FAILED for {did}")
            return None

        try:
            record = AgentRecord.model_validate_json(record_json)
            # CRITICAL: Verify the public key in the record matches the DID
            if not self._verify_did(did, record.public_key_pem):
                print(f"[SDK] SECURITY ALERT: Invalid DID record for {did}. Tampering detected.")
                return None

            return record
        except Exception as e:
            print(f"[SDK] Failed to parse record for {did}: {e}")
            return None

    # --- 4. Network Methods ---

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

        # SPRINT 9: DEMO MODE - Also publish to central cache
        if self.demo_mode:
            cache_record = {
                "did": self.did,
                "endpoint": public_endpoint,
                "public_key_pem": self.public_key_pem,
                "capabilities": capabilities,
                "price": price
            }
            try:
                r = await self.http_client.post(f"{self.registry_url}/publish_record", json=cache_record)
                r.raise_for_status()
                print(f"[DEMO CACHE] Published record to central cache for 100% reliability.")
            except httpx.RequestError as e:
                print(f"WARN: Failed to publish to cache (proceeding with DHT only): {e}")

        # Step 2: Register capabilities with the Indexer
        reg_payload = {
            "agent_id": self.did,  # Use our DID
            "capabilities": capabilities
        }
        try:
            r = await self.http_client.post(f"{self.registry_url}/register_capabilities", json=reg_payload)
            r.raise_for_status()
            print(f"[INDEXER] Successfully registered capabilities for {self.did}.")
        except httpx.RequestError as e:
            print(f"ERROR: Failed to register capabilities. {e}")

    async def _discover(self, target_did: str) -> Optional[AgentRecord]:
        """Discovers another agent's info from the DHT with cache fallback in demo mode."""
        # SPRINT 9: DEMO MODE - Try central cache first
        if self.demo_mode:
            try:
                r = await self.http_client.get(f"{self.registry_url}/discover/{target_did}", timeout=2)
                if r.status_code == 200:
                    record_dict = r.json()
                    record = AgentRecord(
                        public_key_pem=record_dict["public_key_pem"],
                        endpoint=record_dict["endpoint"],
                        price=record_dict["price"],
                        payment_method="none"
                    )
                    # Still verify DID even from cache
                    if self._verify_did(target_did, record.public_key_pem):
                        print(f"[DEMO CACHE] ✅ Found {target_did} in cache (100% reliable)")
                        return record
                    else:
                        print(f"[DEMO CACHE] ❌ DID verification failed for cached record")
            except Exception as e:
                print(f"[DEMO CACHE] Cache lookup failed, falling back to DHT: {e}")

        # Standard DHT lookup (or fallback if cache failed)
        return await self.fetch_record(target_did)

    async def _report_transaction(self, target_did: str, success: bool, response_time_ms: float):
        """Reports the outcome of a transaction to the registry (async)."""
        report = { "agent_id": target_did, "success": success, "response_time_ms": response_time_ms }
        try:
            await self.http_client.post(f"{self.registry_url}/report", json=report, timeout=2)
            print(f"[SDK] Reported transaction for {target_did}. Success: {success}")
        except httpx.RequestError as e:
            print(f"[SDK] WARN: Failed to report transaction: {e}")

    async def send(self, target_did: str, message_body: Dict[str, Any]) -> Dict[str, Any]:
        """Sends a secure, signed P2P message (async)."""
        print(f"Sending message from {self.did} to {target_did}...")

        start_time = time.perf_counter()
        success = False
        response_json = {}

        try:
            target_info = await self._discover(target_did)  # This now verifies the DID
            if not target_info:
                return {"error": "Failed to discover/verify target agent from DHT"}

            payload_data = {
                "sender_did": self.did,
                "body": message_body,
                "timestamp": time.time()
            }
            payload_json = json.dumps(payload_data, sort_keys=True)
            payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')

            signature = self._sign(payload_json.encode('utf-8'))
            signature_b64 = base64.b64encode(signature).decode('utf-8')

            signed_message = { "payload": payload_b64, "signature": signature_b64 }

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
            await self._report_transaction(target_did, success, response_time_ms)

    # --- 5. Economic Decision Engine (async) ---

    async def execute_task(self, capability: str, message_body: Dict[str, Any],
                           policy: Dict[str, float] = None) -> Dict[str, Any]:
        """Finds the BEST agent for a capability and sends it a message."""
        print(f"\n[SDK] Searching for agent with capability: '{capability}'")

        if policy is None:
            policy = self.default_policy

        # --- Step 1: Search Indexer ---
        try:
            r = await self.http_client.get(f"{self.registry_url}/search", params={"capability": capability})
            r.raise_for_status()
            did_list = r.json()  # List[str] of DIDs
        except httpx.RequestError as e:
            return {"error": f"Failed to search for capability: {e}"}

        if not did_list:
            return {"error": f"No agents found with capability: {capability}"}

        print(f"[SDK] Found {len(did_list)} candidates from Indexer: {did_list}")

        # --- Step 2 & 3: Fetch Data (DHT) and Reputations (Indexer) in Parallel ---
        try:
            # Fetch all agent records from DHT (with verification)
            record_tasks = [self._discover(did) for did in did_list]  # _discover now verifies

            # Fetch all reputations from Indexer
            rep_task = self.http_client.post(f"{self.registry_url}/get_reputations",
                                           json={"agent_ids": did_list})

            # Run all lookups concurrently
            results = await asyncio.gather(*record_tasks, rep_task)

            records = results[:-1]  # List[Optional[AgentRecord]]
            rep_response = results[-1].json()

            # Parse reputation data
            reputations = {}
            for did, stats_dict in rep_response['reputations'].items():
                reputations[did] = ReputationStats(**stats_dict)

        except (httpx.RequestError, json.JSONDecodeError) as e:
            return {"error": f"Failed during data/reputation fetching: {e}"}

        # --- Step 4: Rank Candidates ---
        candidates_data = []
        for i, record in enumerate(records):
            if record:  # Check if DHT lookup AND verification was successful
                did = did_list[i]
                candidates_data.append({
                    "did": did,  # Use DID as the key
                    "price": record.price,
                    "reputation": reputations[did].reputation_score
                })
                print(f"[SDK] Verified candidate: {did[:20]}... - Price: ${record.price}, Rep: {reputations[did].reputation_score:.2f}")
            else:
                print(f"[SDK] Discarding invalid/unfound candidate: {did_list[i]}")

        if not candidates_data:
            return {"error": "Found agent DIDs but failed to fetch/verify any records from DHT."}

        if len(candidates_data) == 1:
            winner_did = candidates_data[0]['did']
            print(f"[SDK] Only one verified candidate: {winner_did}")
        else:
            print(f"\\n[SDK] Ranking {len(candidates_data)} verified candidates by policy: Price={policy.get('price', 0.5)*100:.0f}%, Reputation={policy.get('reputation', 0.5)*100:.0f}%")

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
                print(f"  - {c['did'][:20]}...: Price=${c['price']:.2f}, Rep={c['reputation']:.2f}, Utility={utility_score:.3f}")

            # Sort by highest utility
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            winner_did = scored_candidates[0][1]['did']

        print(f"\\n[SDK] Winner selected: {winner_did}")

        # --- Step 5: Send message to winner ---
        return await self.send(target_did=winner_did, message_body=message_body)

    # --- 6. Listener ---

    def on_message(self, func: Callable):
        """Decorator to register the user's message handler."""
        self._message_handler = func
        return func

    def _create_listener_app(self):
        """Creates the internal FastAPI app for this agent."""
        app = FastAPI(title=f"Agent Listener: {self.did}")

        @app.post("/invoke")
        async def handle_invoke(message: SignedMessage, request: Request):
            if not self._message_handler:
                raise HTTPException(status_code=500, detail="Agent has no message handler")

            try:
                payload_json = base64.b64decode(message.payload).decode('utf-8')
                signature = base64.b64decode(message.signature)
                payload: Dict = json.loads(payload_json)
                sender_did = payload['sender_did']
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid message format: {e}")

            # Discover sender (using hybrid cache) to get their public key
            # This step now ALSO verifies the sender's DID
            sender_record = await self._discover(sender_did)
            if not sender_record:
                raise HTTPException(status_code=403, detail="Could not discover/verify sender identity from DHT")

            # Verify the message signature
            is_valid = self._verify(
                payload_json.encode('utf-8'),
                signature,
                sender_record.public_key_pem
            )

            if not is_valid:
                raise HTTPException(status_code=403, detail="Invalid signature")

            print(f"Received valid message from {sender_did[:20]}...")
            # Call the user's handler (can be sync or async)
            result = self._message_handler(sender_did, payload['body'])
            # Check if it's a coroutine and await if needed
            if hasattr(result, '__await__'):
                response_body = await result
            else:
                response_body = result
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

        print(f"\\n--- Agent {self.did} is LIVE ---")
        print(f"--- HTTP listener on {http_host}:{http_port} ---")
        print(f"--- DHT node on {dht_host}:{dht_port} ---\\n")

        # 3. Run the server
        await server.serve()