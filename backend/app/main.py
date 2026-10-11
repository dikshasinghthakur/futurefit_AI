import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import admin, analyses, auth, catalog, dashboard, profile, resumes, roadmaps
from app.core import database
from app.core.config import get_settings
from app.seed import seed
from app.services.taxonomy_cache import get_taxonomy

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("futurefit")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.jwt_secret.startswith("dev-only") or settings.jwt_secret.startswith("change-me"):
        log.warning("JWT_SECRET is a placeholder — set a strong secret before deploying.")
    db = await database.connect()
    await database.ensure_indexes(db)
    if settings.seed_on_startup:
        await seed(db)
    await get_taxonomy(db)  # warm the in-memory taxonomy + TF-IDF similarity matrix
    log.info("FutureFit AI ready")
    yield
    await database.close()


app = FastAPI(title="FutureFit AI API", version="1.0.0", lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(GZipMiddleware, minimum_size=1024)
settings = get_settings()
allowed_origins = settings.cors_origins.copy()
if settings.frontend_host:
    allowed_origins.append(f"https://{settings.frontend_host}")
app.add_middleware(
    CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.middleware("http")
async def timing_and_security_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


@app.get("/api/health", tags=["meta"])
async def health():
    await database.get_db().command("ping")
    return {"status": "ok"}


for r in (auth.router, profile.router, resumes.router, catalog.router, analyses.router,
          roadmaps.router, dashboard.router, admin.router):
    app.include_router(r, prefix="/api")
