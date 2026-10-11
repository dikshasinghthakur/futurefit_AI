import re

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.utils import Page, paged, serialize
from app.deps import current_user, db_dep
from app.services.taxonomy_cache import get_taxonomy

router = APIRouter(tags=["catalog"], dependencies=[Depends(current_user)])


@router.get("/roles")
async def list_roles(q: str | None = Query(None, max_length=60), db=Depends(db_dep)):
    flt = {"$or": [{"title": {"$regex": re.escape(q), "$options": "i"}}, {"description": {"$regex": re.escape(q), "$options": "i"}}]} if q else {}
    docs = await db.roles.find(flt, {"skills": 0}).sort("title", 1).to_list(200)
    return serialize(docs)


@router.get("/roles/{slug}")
async def get_role(slug: str, db=Depends(db_dep)):
    role = await db.roles.find_one({"slug": slug})
    if not role:
        raise HTTPException(404, "Role not found")
    tax = await get_taxonomy(db)
    for s in role["skills"]:
        s["name"], s["category"] = tax.name(s["skill"]), tax.category(s["skill"])
    role["skills"].sort(key=lambda s: -s["weight"])
    return serialize(role)


@router.get("/skills")
async def list_skills(q: str | None = Query(None, max_length=60), category: str | None = None, db=Depends(db_dep)):
    flt: dict = {}
    if category:
        flt["category"] = category
    if q:
        flt["name"] = {"$regex": re.escape(q), "$options": "i"}
    return serialize(await db.skills.find(flt, {"_id": 0, "created_at": 0}).sort("name", 1).to_list(500))


@router.get("/courses")
async def list_courses(
    p: Page = Depends(), skill: str | None = None, level: str | None = None, free: bool | None = None,
    q: str | None = Query(None, max_length=60), curated: bool | None = None, db=Depends(db_dep),
):
    flt: dict = {}
    if skill:
        flt["skill_ids"] = skill
    if level:
        flt["level"] = level
    if free is not None:
        flt["free"] = free
    if curated is not None:
        flt["curated"] = curated
    if q:
        flt["title"] = {"$regex": re.escape(q), "$options": "i"}
    total = await db.courses.count_documents(flt)
    docs = await db.courses.find(flt).sort([("curated", -1), ("title", 1)]).skip(p.skip).limit(p.page_size).to_list(p.page_size)
    tax = await get_taxonomy(db)
    items = serialize(docs)
    for c in items:
        c["skills"] = [{"slug": s, "name": tax.name(s)} for s in c.get("skill_ids", [])]
    return paged(items, total, p)
