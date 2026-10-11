import asyncio

from app.services.taxonomy import SkillTaxonomy

_taxonomy: SkillTaxonomy | None = None
_lock = asyncio.Lock()


async def get_taxonomy(db) -> SkillTaxonomy:
    """Taxonomy is small and read-mostly: build once, keep in memory, rebuild after admin edits."""
    global _taxonomy
    if _taxonomy is None:
        async with _lock:
            if _taxonomy is None:
                skills = await db.skills.find({}, {"_id": 0, "created_at": 0}).to_list(length=2000)
                _taxonomy = SkillTaxonomy(skills)
    return _taxonomy


def invalidate_taxonomy() -> None:
    global _taxonomy
    _taxonomy = None
