from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, Query


def to_oid(value: str, label: str = "Resource") -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(404, f"{label} not found")


def serialize(value):
    """Mongo document -> JSON-safe structure (_id -> id, ObjectId -> str). datetimes are handled by FastAPI."""
    if isinstance(value, dict):
        return {("id" if k == "_id" else k): serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(v) for v in value]
    if isinstance(value, ObjectId):
        return str(value)
    return value


class Page:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
        self.page, self.page_size = page, page_size
        self.skip = (page - 1) * page_size


def paged(items: list, total: int, p: Page) -> dict:
    return {"items": items, "total": total, "page": p.page, "page_size": p.page_size,
            "pages": max(1, -(-total // p.page_size))}
