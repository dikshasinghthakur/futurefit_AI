import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.utils import serialize, to_oid
from app.deps import db_dep, require_admin
from app.schemas import CourseUpsert, RoleUpsert, SkillUpsert
from app.services.taxonomy_cache import get_taxonomy, invalidate_taxonomy

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats")
async def stats(db=Depends(db_dep)):
    names = ["users", "resumes", "analyses", "roadmaps", "skills", "roles", "courses", "progress_events"]
    counts = await asyncio.gather(*[db[n].estimated_document_count() for n in names])
    avg = await db.analyses.aggregate([{"$group": {"_id": None, "avg": {"$avg": "$readiness_score"}}}]).to_list(1)
    top_roles = await db.analyses.aggregate(
        [{"$group": {"_id": "$role_title", "n": {"$sum": 1}, "avg": {"$avg": "$readiness_score"}}}, {"$sort": {"n": -1}}, {"$limit": 5}]
    ).to_list(5)
    return {"counts": dict(zip(names, counts)), "avg_readiness": round(avg[0]["avg"], 1) if avg else None,
            "top_roles": [{"role": r["_id"], "analyses": r["n"], "avg_readiness": round(r["avg"], 1)} for r in top_roles]}


@router.put("/skills/{slug}")
async def upsert_skill(slug: str, body: SkillUpsert, db=Depends(db_dep)):
    if body.slug != slug:
        raise HTTPException(422, "Slug in path and body must match")
    tax = await get_taxonomy(db)
    unknown = [r for r in body.prerequisites + body.related if r not in tax.skills and r != slug]
    if unknown:
        raise HTTPException(422, f"Unknown skills referenced: {', '.join(unknown)}")
    await db.skills.update_one({"slug": slug}, {"$set": body.model_dump(), "$setOnInsert": {"created_at": datetime.now(timezone.utc)}}, upsert=True)
    invalidate_taxonomy()
    return {"ok": True}


@router.put("/roles/{slug}")
async def upsert_role(slug: str, body: RoleUpsert, db=Depends(db_dep)):
    if body.slug != slug:
        raise HTTPException(422, "Slug in path and body must match")
    tax = await get_taxonomy(db)
    unknown = {x for s in body.skills for x in [s.skill, *s.alt] if x not in tax.skills}
    if unknown:
        raise HTTPException(422, f"Unknown skills referenced: {', '.join(sorted(unknown))}")
    await db.roles.update_one({"slug": slug}, {"$set": body.model_dump(), "$setOnInsert": {"created_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"ok": True}


@router.delete("/roles/{slug}", status_code=204)
async def delete_role(slug: str, db=Depends(db_dep)):
    if not (await db.roles.delete_one({"slug": slug})).deleted_count:
        raise HTTPException(404, "Role not found")


@router.post("/courses", status_code=201)
async def create_course(body: CourseUpsert, db=Depends(db_dep)):
    tax = await get_taxonomy(db)
    unknown = [s for s in body.skill_ids if s not in tax.skills]
    if unknown:
        raise HTTPException(422, f"Unknown skills referenced: {', '.join(unknown)}")
    res = await db.courses.insert_one({**body.model_dump(), "curated": True, "created_at": datetime.now(timezone.utc)})
    return {"id": str(res.inserted_id)}


@router.delete("/courses/{course_id}", status_code=204)
async def delete_course(course_id: str, db=Depends(db_dep)):
    if not (await db.courses.delete_one({"_id": to_oid(course_id, "Course")})).deleted_count:
        raise HTTPException(404, "Course not found")
