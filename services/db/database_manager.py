import os
import asyncio
from neo4j import AsyncGraphDatabase
from motor.motor_asyncio import AsyncIOMotorClient

class DatabaseManager:
    _neo4j_driver = None
    _mongo_client = None
    _db = None

    @classmethod
    async def init_neo4j(cls):
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USERNAME")
        password = os.environ.get("NEO4J_PASSWORD")
        
        if not uri or not user or not password:
            print("[NEMESIS OMEGA DB] Neo4j credentials not found in environment. Graph storage disabled.")
            return

        try:
            cls._neo4j_driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            await asyncio.wait_for(cls._neo4j_driver.verify_connectivity(), timeout=5.0)
            print("[NEMESIS OMEGA DB] Connected to Neo4j (Aura) Database.")
        except asyncio.TimeoutError:
            print("[NEMESIS OMEGA DB] Timeout connecting to Neo4j. Graph storage disabled.")
            cls._neo4j_driver = None
        except Exception as e:
            print(f"[NEMESIS OMEGA DB] Failed to connect to Neo4j (suppressed): {type(e).__name__}")
            cls._neo4j_driver = None

    @classmethod
    async def init_mongo(cls):
        uri = os.environ.get("MONGODB_URI")
        if not uri:
            print("[NEMESIS OMEGA DB] MongoDB URI not found in environment. Document storage disabled.")
            return
            
        try:
            cls._mongo_client = AsyncIOMotorClient(uri)
            # Ping the database to verify connection
            await cls._mongo_client.admin.command('ping')
            cls._db = cls._mongo_client.get_database("nemesisdb")
            print("[NEMESIS OMEGA DB] Connected to MongoDB Atlas.")
        except Exception as e:
            print(f"[NEMESIS OMEGA DB] Failed to connect to MongoDB: {e}")
            cls._mongo_client = None

    @classmethod
    async def initialize_all(cls):
        await asyncio.gather(
            cls.init_neo4j(),
            cls.init_mongo()
        )

    @classmethod
    async def close_all(cls):
        if cls._neo4j_driver:
            await cls._neo4j_driver.close()
            print("[NEMESIS OMEGA DB] Neo4j connection closed.")
        if cls._mongo_client:
            cls._mongo_client.close()
            print("[NEMESIS OMEGA DB] MongoDB connection closed.")

    # --- Data Ingestion Methods ---
    
    @classmethod
    async def insert_trace_job(cls, job_id: str, payload: dict):
        if cls._db is not None:
            await cls._db.trace_jobs.update_one(
                {"job_id": job_id},
                {"$set": payload},
                upsert=True
            )
            
    @classmethod
    async def add_graph_node(cls, node_id: str, properties: dict):
        if cls._neo4j_driver:
            query = (
                "MERGE (n:Wallet {id: $id}) "
                "SET n += $props"
            )
            async with cls._neo4j_driver.session() as session:
                await session.run(query, id=node_id, props=properties)

    @classmethod
    async def add_graph_edge(cls, from_id: str, to_id: str, properties: dict):
        if cls._neo4j_driver:
            query = (
                "MATCH (a:Wallet {id: $from_id}) "
                "MATCH (b:Wallet {id: $to_id}) "
                "MERGE (a)-[r:TRANSFERRED]->(b) "
                "SET r += $props"
            )
            async with cls._neo4j_driver.session() as session:
                await session.run(query, from_id=from_id, to_id=to_id, props=properties)
