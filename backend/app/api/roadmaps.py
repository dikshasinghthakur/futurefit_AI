from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ReturnDocument

from app.core.utils import Page, paged, serialize, to_oid
from app.deps import current_user, db_dep
from app.schemas import ItemToggleIn, RoadmapIn
from app.services.roadmap import build_roadmap, compute_progress, plan_targets
from app.services.taxonomy_cache import get_taxonomy

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])
_LIST_PROJECTION = {"phases": 0}


@router.post("", status_code=201)
async def create_roadmap(body: RoadmapIn, user=Depends(current_user), db=Depends(db_dep)):
    analysis = await db.analyses.find_one({"_id": to_oid(body.analysis_id, "Analysis"), "user_id": user["_id"]})
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    role = await db.roles.find_one({"slug": analysis["role_slug"]}, {"project_idea": 1})
    tax = await get_taxonomy(db)

    cands = plan_targets(tax, analysis, owned=set(analysis.get("owned_skills", [])))
    courses = await db.courses.find({"skill_ids": {"$in": [c["skill"] for c in cands]}}).to_list(2000) if cands else []
    plan = build_roadmap(tax, cands, courses, body.hours_per_week, (role or {}).get("project_idea"))
    if not plan["phases"]:
        raise HTTPException(422, "No skill gaps found for this analysis — nothing to plan. Great job!")

    now = datetime.now(timezone.utc)
    doc = {"user_id": user["_id"], "analysis_id": analysis["_id"], "role_slug": analysis["role_slug"],
           "role_title": analysis["role_title"], "start_readiness": analysis["readiness_score"],
           **plan, **compute_progress(plan["phases"]), "created_at": now, "updated_at": now}
    res = await db.roadmaps.insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)


@router.get("")
async def list_roadmaps(p: Page = Depends(), user=Depends(current_user), db=Depends(db_dep)):
    q = {"user_id": user["_id"]}
    cur = db.roadmaps.find(q, _LIST_PROJECTION).sort("created_at", -1).skip(p.skip).limit(p.page_size)
    return paged(serialize(await cur.to_list(p.page_size)), await db.roadmaps.count_documents(q), p)


@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: str, user=Depends(current_user), db=Depends(db_dep)):
    doc = await db.roadmaps.find_one({"_id": to_oid(roadmap_id, "Roadmap"), "user_id": user["_id"]})
    if not doc:
        raise HTTPException(404, "Roadmap not found")
    return serialize(doc)


@router.patch("/{roadmap_id}/items/{item_id}")
async def toggle_item(roadmap_id: str, item_id: str, body: ItemToggleIn, user=Depends(current_user), db=Depends(db_dep)):
    rid, now = to_oid(roadmap_id, "Roadmap"), datetime.now(timezone.utc)
    # One atomic update targets exactly the nested item via array filters (no read-modify-write race).
    updated = await db.roadmaps.find_one_and_update(
        {"_id": rid, "user_id": user["_id"], "phases.items.id": item_id},
        {"$set": {"phases.$[].items.$[it].completed": body.completed,
                  "phases.$[].items.$[it].completed_at": now if body.completed else None, "updated_at": now}},
        array_filters=[{"it.id": item_id}], return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(404, "Roadmap item not found")

    progress = compute_progress(updated["phases"])
    await db.roadmaps.update_one({"_id": rid}, {"$set": progress})
    updated.update(progress)

    item = next(i for p in updated["phases"] for i in p["items"] if i["id"] == item_id)
    if body.completed:  # idempotent thanks to the partial unique index
        await db.progress_events.update_one(
            {"roadmap_id": rid, "item_id": item_id, "type": "item_completed"},
            {"$setOnInsert": {"user_id": user["_id"], "skill_slug": item.get("skill_slug"), "hours": item["est_hours"], "created_at": now}},
            upsert=True)
    else:
        await db.progress_events.delete_one({"roadmap_id": rid, "item_id": item_id, "type": "item_completed"})
    return serialize(updated)


@router.delete("/{roadmap_id}", status_code=204)
async def delete_roadmap(roadmap_id: str, user=Depends(current_user), db=Depends(db_dep)):
    rid = to_oid(roadmap_id, "Roadmap")
    res = await db.roadmaps.delete_one({"_id": rid, "user_id": user["_id"]})
    if not res.deleted_count:
        raise HTTPException(404, "Roadmap not found")
    await db.progress_events.delete_many({"roadmap_id": rid, "user_id": user["_id"]})
