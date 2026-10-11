"""Idempotent seeding: inserts only what is missing, so admin edits are never overwritten."""
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus

from pymongo import UpdateOne

from app.core.config import get_settings
from app.core.security import hash_password
from app.data.courses import CURATED
from app.data.roles import ROLES
from app.data.skills import SKILLS

log = logging.getLogger("futurefit.seed")


def _fallback_courses():
    """Generic search links for skills without a curated resource (clearly flagged curated=False)."""
    covered = {c[0] for c in CURATED}
    out = []
    for s in SKILLS:
        if s["slug"] in covered:
            continue
        q = quote_plus(f"{s['name']} tutorial")
        out.append((s["slug"], f"{s['name']}: find a course", "Web search",
                    f"https://www.google.com/search?q={q}", "beginner", s["hours"], True, False))
    return out


async def seed(db):
    now = datetime.now(timezone.utc)

    ops = [UpdateOne({"slug": s["slug"]}, {"$setOnInsert": {**s, "created_at": now}}, upsert=True) for s in SKILLS]
    await db.skills.bulk_write(ops, ordered=False)

    ops = [UpdateOne({"slug": r["slug"]}, {"$setOnInsert": {**r, "created_at": now}}, upsert=True) for r in ROLES]
    await db.roles.bulk_write(ops, ordered=False)

    rows = [(*c, True) for c in CURATED] + _fallback_courses()
    ops = []
    for skill, title, provider, url, level, hours, free, curated in rows:
        doc = {"title": title, "provider": provider, "url": url, "level": level, "hours": hours,
               "free": free, "curated": curated, "skill_ids": [skill]}
        ops.append(UpdateOne({"url": url, "skill_ids": [skill]}, {"$setOnInsert": {**doc, "created_at": now}}, upsert=True))
    await db.courses.bulk_write(ops, ordered=False)

    settings = get_settings()
    if settings.admin_email and settings.admin_password:
        email = settings.admin_email.lower()
        if not await db.users.find_one({"email": email}, {"_id": 1}):
            await db.users.insert_one({
                "name": "Administrator", "email": email, "role": "admin",
                "password_hash": hash_password(settings.admin_password),
                "profile": {}, "created_at": now, "last_login_at": None,
            })
            log.info("Bootstrap admin created: %s", email)
    log.info("Seed complete: %d skills, %d roles, %d courses", len(SKILLS), len(ROLES), len(rows))
