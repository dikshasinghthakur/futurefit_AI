from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import public_user
from app.deps import current_user, db_dep
from app.schemas import ProfileIn

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(user=Depends(current_user)):
    return user.get("profile", {})


@router.put("")
async def update_profile(body: ProfileIn, user=Depends(current_user), db=Depends(db_dep)):
    data = body.model_dump()
    if data.get("target_role_slug") and not await db.roles.find_one({"slug": data["target_role_slug"]}, {"_id": 1}):
        raise HTTPException(422, "Unknown target role")
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"profile": data}})
    updated = await db.users.find_one({"_id": user["_id"]}, {"password_hash": 0})
    return public_user(updated)
