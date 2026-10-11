from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.core.utils import Page, paged, serialize, to_oid
from app.deps import current_user, db_dep
from app.schemas import ResumeTextIn
from app.services import llm
from app.services.skill_extractor import parse_resume
from app.services.taxonomy_cache import get_taxonomy
from app.services.text_extract import EmptyDocument, UnsupportedFileType, extract_text

router = APIRouter(prefix="/resumes", tags=["resumes"])
_LIST_PROJECTION = {"text": 0, "parsed.skills.evidence": 0}


async def _create(db, user, title: str, text: str, meta: dict) -> dict:
    s = get_settings()
    if await db.resumes.count_documents({"user_id": user["_id"]}) >= s.max_resumes_per_user:
        raise HTTPException(409, f"Resume limit reached ({s.max_resumes_per_user}). Delete an old one first.")
    tax = await get_taxonomy(db)
    parsed = await run_in_threadpool(parse_resume, text, tax)  # regex/NLP is CPU-bound -> keep the event loop free

    known = {x["slug"] for x in parsed["skills"]}
    for slug in await llm.extra_skills(text, tax.slugs):  # no-op unless an API key is configured
        if slug not in known:
            sk = tax.get(slug)
            parsed["skills"].append({"slug": slug, "name": sk["name"], "category": sk["category"], "mentions": 1,
                                     "confidence": 0.6, "evidence": ["llm"], "source": "llm"})

    doc = {"user_id": user["_id"], "title": title, **meta, "text": text, "parsed": parsed,
           "created_at": datetime.now(timezone.utc)}
    res = await db.resumes.insert_one(doc)
    doc["_id"] = res.inserted_id
    doc.pop("text")
    return serialize(doc)


@router.post("", status_code=201)
async def upload_resume(file: UploadFile = File(...), user=Depends(current_user), db=Depends(db_dep)):
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File too large (max {get_settings().max_upload_mb} MB)")
    try:
        text = await run_in_threadpool(extract_text, file.filename or "resume.txt", data)
    except (UnsupportedFileType, EmptyDocument) as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(422, "This file looks corrupted or isn't a valid document.")
    return await _create(db, user, file.filename or "Resume", text,
                         {"filename": file.filename, "size": len(data), "content_type": file.content_type})


@router.post("/text", status_code=201)
async def paste_resume(body: ResumeTextIn, user=Depends(current_user), db=Depends(db_dep)):
    return await _create(db, user, body.title, body.text, {"filename": None, "size": len(body.text), "content_type": "text/plain"})


@router.get("")
async def list_resumes(p: Page = Depends(), user=Depends(current_user), db=Depends(db_dep)):
    q = {"user_id": user["_id"]}
    cur = db.resumes.find(q, _LIST_PROJECTION).sort("created_at", -1).skip(p.skip).limit(p.page_size)
    return paged(serialize(await cur.to_list(p.page_size)), await db.resumes.count_documents(q), p)


@router.get("/{resume_id}")
async def get_resume(resume_id: str, user=Depends(current_user), db=Depends(db_dep)):
    doc = await db.resumes.find_one({"_id": to_oid(resume_id), "user_id": user["_id"]}, {"text": 0})
    if not doc:
        raise HTTPException(404, "Resume not found")
    return serialize(doc)


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str, user=Depends(current_user), db=Depends(db_dep)):
    res = await db.resumes.delete_one({"_id": to_oid(resume_id), "user_id": user["_id"]})
    if not res.deleted_count:
        raise HTTPException(404, "Resume not found")
