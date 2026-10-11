from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pymongo.errors import DuplicateKeyError

from app.core.ratelimit import rate_limit
from app.core.security import DUMMY_HASH, create_token, decode_token, hash_password, verify_password
from app.core.utils import to_oid
from app.deps import current_user, db_dep
from app.schemas import LoginIn, RefreshIn, RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])


def public_user(u: dict) -> dict:
    return {"id": str(u["_id"]), "name": u["name"], "email": u["email"], "role": u.get("role", "user"),
            "profile": u.get("profile", {}), "created_at": u.get("created_at")}


def _tokens(u: dict) -> dict:
    uid, role = str(u["_id"]), u.get("role", "user")
    return {"access_token": create_token(uid, role, "access"), "refresh_token": create_token(uid, role, "refresh"),
            "token_type": "bearer", "user": public_user(u)}


@router.post("/register", status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def register(body: RegisterIn, db=Depends(db_dep)):
    doc = {"name": body.name, "email": body.email.lower(), "role": "user", "profile": {},
           "password_hash": await run_in_threadpool(hash_password, body.password),  # bcrypt is CPU-bound
           "created_at": datetime.now(timezone.utc), "last_login_at": None}
    try:
        res = await db.users.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(409, "An account with this email already exists")
    doc["_id"] = res.inserted_id
    return _tokens(doc)


@router.post("/login", dependencies=[Depends(rate_limit(15, 60))])
async def login(body: LoginIn, db=Depends(db_dep)):
    user = await db.users.find_one({"email": body.email.lower()})
    # Always run a hash comparison so response time doesn't reveal whether the email exists.
    ok = await run_in_threadpool(verify_password, body.password, user["password_hash"] if user else DUMMY_HASH)
    if not user or not ok:
        raise HTTPException(401, "Incorrect email or password")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login_at": datetime.now(timezone.utc)}})
    return _tokens(user)


@router.post("/refresh", dependencies=[Depends(rate_limit(30, 60))])
async def refresh(body: RefreshIn, db=Depends(db_dep)):
    payload = decode_token(body.refresh_token, "refresh")
    user = await db.users.find_one({"_id": to_oid(payload["sub"], "User")})
    if not user:
        raise HTTPException(401, "User no longer exists")
    return _tokens(user)


@router.get("/me")
async def me(user=Depends(current_user)):
    return public_user(user)
