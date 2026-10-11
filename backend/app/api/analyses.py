from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.utils import Page, paged, serialize, to_oid
from app.deps import current_user, db_dep
from app.schemas import AnalysisIn
from app.services import llm
from app.services.gap_analysis import analyze_gap
from app.services.taxonomy_cache import get_taxonomy

router = APIRouter(prefix="/analyses", tags=["analyses"])
_SUMMARY = {"matched": 0, "partial": 0, "missing": 0, "owned_skills": 0, "coach_note": 0, "category_breakdown": 0}


async def acquired_skills(db, user_id) -> set[str]:
    """Skills the user has *completed* in any roadmap — closes the feedback loop (step 8 of the methodology)."""
    pipeline = [
        {"$match": {"user_id": user_id}}, {"$unwind": "$phases"}, {"$unwind": "$phases.items"},
        {"$match": {"phases.items.completed": True, "phases.items.skill_slug": {"$ne": None}}},
        {"$group": {"_id": "$phases.items.skill_slug"}},
    ]
    return {d["_id"] async for d in db.roadmaps.aggregate(pipeline)}


@router.post("", status_code=201)
async def create_analysis(body: AnalysisIn, user=Depends(current_user), db=Depends(db_dep)):
    resume = await db.resumes.find_one({"_id": to_oid(body.resume_id, "Resume"), "user_id": user["_id"]}, {"text": 0})
    if not resume:
        raise HTTPException(404, "Resume not found")
    role = await db.roles.find_one({"slug": body.role_slug})
    if not role:
        raise HTTPException(404, "Role not found")

    tax = await get_taxonomy(db)
    user_skills = {s["slug"]: s["confidence"] for s in resume["parsed"]["skills"]}
    acquired = await acquired_skills(db, user["_id"])
    for slug in acquired:
        user_skills[slug] = max(user_skills.get(slug, 0), 0.8)

    result = analyze_gap(tax, user_skills, role)
    note = await llm.coach_note(role["title"], result["readiness_score"], [m["name"] for m in result["matched"]],
                                [tax.name(s) for s in result["top_gaps"]])
    doc = {
        "user_id": user["_id"], "resume_id": resume["_id"], "resume_title": resume.get("title"),
        "role_slug": role["slug"], "role_title": role["title"], **result,
        "owned_skills": sorted(user_skills), "acquired_skills": sorted(acquired), "coach_note": note,
        "created_at": datetime.now(timezone.utc),
    }
    res = await db.analyses.insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)


@router.get("")
async def list_analyses(p: Page = Depends(), user=Depends(current_user), db=Depends(db_dep)):
    q = {"user_id": user["_id"]}
    cur = db.analyses.find(q, _SUMMARY).sort("created_at", -1).skip(p.skip).limit(p.page_size)
    return paged(serialize(await cur.to_list(p.page_size)), await db.analyses.count_documents(q), p)


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str, user=Depends(current_user), db=Depends(db_dep)):
    doc = await db.analyses.find_one({"_id": to_oid(analysis_id, "Analysis"), "user_id": user["_id"]})
    if not doc:
        raise HTTPException(404, "Analysis not found")
    return serialize(doc)


@router.delete("/{analysis_id}", status_code=204)
async def delete_analysis(analysis_id: str, user=Depends(current_user), db=Depends(db_dep)):
    res = await db.analyses.delete_one({"_id": to_oid(analysis_id, "Analysis"), "user_id": user["_id"]})
    if not res.deleted_count:
        raise HTTPException(404, "Analysis not found")
