"""MongoDB connection + schema/index definitions.

Collections (see README for the full data model):
  users            1 doc/user, profile embedded (1:1, always read together)
  resumes          N per user; parsed skills embedded, raw file NOT stored (only extracted text)
  skills           taxonomy (global, small, cached in memory)
  roles            target roles w/ weighted skill requirements embedded (read as one unit)
  courses          learning resources, indexed by skill
  analyses         immutable snapshots of a gap analysis (enables trend over time)
  roadmaps         phases/items embedded (always loaded + updated together, bounded size)
  progress_events  append-only activity log -> dashboards (unbounded, so kept separate)
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT

from app.core.config import get_settings


class _Mongo:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongo = _Mongo()


async def connect() -> AsyncIOMotorDatabase:
    s = get_settings()
    mongo.client = AsyncIOMotorClient(
        s.mongo_uri, maxPoolSize=s.mongo_max_pool, serverSelectionTimeoutMS=5000, tz_aware=True
    )
    mongo.db = mongo.client[s.mongo_db]
    await mongo.client.admin.command("ping")
    return mongo.db


async def close() -> None:
    if mongo.client:
        mongo.client.close()


def get_db() -> AsyncIOMotorDatabase:
    assert mongo.db is not None, "Database not initialised"
    return mongo.db


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.users.create_index("email", unique=True)

    await db.resumes.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

    await db.skills.create_index("slug", unique=True)
    await db.skills.create_index("category")

    await db.roles.create_index("slug", unique=True)
    await db.roles.create_index([("title", TEXT), ("description", TEXT)])

    await db.courses.create_index("skill_ids")  # multikey
    await db.courses.create_index([("level", ASCENDING), ("free", ASCENDING)])
    await db.courses.create_index([("title", TEXT), ("provider", TEXT)])

    await db.analyses.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

    await db.roadmaps.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await db.roadmaps.create_index("analysis_id")

    await db.progress_events.create_index([("user_id", ASCENDING), ("type", ASCENDING), ("created_at", DESCENDING)])
    # one 'item_completed' event per roadmap item -> idempotent toggling
    await db.progress_events.create_index(
        [("roadmap_id", ASCENDING), ("item_id", ASCENDING)],
        unique=True, partialFilterExpression={"type": "item_completed"},
    )
