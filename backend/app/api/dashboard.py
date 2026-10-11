import asyncio
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.core.utils import serialize
from app.deps import current_user, db_dep

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def dashboard(user=Depends(current_user), db=Depends(db_dep)):
    """One round-trip for the whole dashboard; independent queries run concurrently, all index-backed."""
    uid = user["_id"]
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=29)

    async def latest(coll, proj=None):
        return await coll.find_one({"user_id": uid}, proj, sort=[("created_at", -1)])

    async def trend():
        docs = await db.analyses.find({"user_id": uid}, {"readiness_score": 1, "role_title": 1, "created_at": 1}) \
            .sort("created_at", -1).limit(12).to_list(12)
        return list(reversed(docs))

    async def activity():
        pipeline = [
            {"$match": {"user_id": uid, "type": "item_completed", "created_at": {"$gte": since}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                        "count": {"$sum": 1}, "hours": {"$sum": "$hours"}}},
        ]
        return {d["_id"]: d async for d in db.progress_events.aggregate(pipeline)}

    (n_resumes, n_analyses, n_done, analysis, roadmap, resume, trend_docs, act) = await asyncio.gather(
        db.resumes.count_documents({"user_id": uid}),
        db.analyses.count_documents({"user_id": uid}),
        db.progress_events.count_documents({"user_id": uid, "type": "item_completed"}),
        latest(db.analyses, {"matched": 0, "partial": 0, "missing": 0, "owned_skills": 0}),
        latest(db.roadmaps),
        latest(db.resumes, {"parsed.skills.category": 1, "title": 1}),
        trend(), activity(),
    )

    days = [(since + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
    active_roadmap = None
    if roadmap:
        nxt = [{"id": i["id"], "skill_name": i["skill_name"], "est_hours": i["est_hours"], "type": i["type"],
                "course": i.get("course")} for p in roadmap["phases"] for i in p["items"] if not i["completed"]][:4]
        active_roadmap = {"id": str(roadmap["_id"]), "role_title": roadmap["role_title"], "progress_pct": roadmap["progress_pct"],
                          "completed_items": roadmap["completed_items"], "total_items": roadmap["total_items"],
                          "estimated_weeks": roadmap["estimated_weeks"], "next_items": nxt}

    cats = Counter(s["category"] for s in (resume or {}).get("parsed", {}).get("skills", []))
    return {
        "stats": {
            "resumes": n_resumes, "analyses": n_analyses, "completed_items": n_done,
            "readiness": analysis["readiness_score"] if analysis else None,
            "roadmap_progress": active_roadmap["progress_pct"] if active_roadmap else None,
            "hours_learned": sum(d["hours"] for d in act.values()),
        },
        "latest_analysis": serialize(analysis) if analysis else None,
        "readiness_trend": [{"date": d["created_at"], "score": d["readiness_score"], "role_title": d["role_title"]} for d in trend_docs],
        "activity": [{"date": d, "count": act.get(d, {}).get("count", 0)} for d in days],
        "active_roadmap": active_roadmap,
        "skills_by_category": dict(cats),
    }
