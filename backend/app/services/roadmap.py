"""Roadmap planner: gaps -> prerequisite-aware learning order -> time-boxed phases with course picks."""
from __future__ import annotations

import math
import uuid

from app.services.taxonomy import SkillTaxonomy


def plan_targets(tax: SkillTaxonomy, analysis: dict, owned: set[str]) -> list[dict]:
    """Candidates = missing + partial skills + any prerequisite the user doesn't own yet."""
    cands: dict[str, dict] = {}
    for item in analysis["missing"] + analysis["partial"]:
        cands[item["skill"]] = {
            "skill": item["skill"], "status": item["status"], "priority": item["weight"] * (1 - item["score"]),
            "reason": f"{'Partially covered' if item['status'] == 'partial' else 'Missing'} — importance {item['weight']}/5 for this role",
            "prerequisite_of": None,
        }
    for c in list(cands.values()):
        for pre in tax.prerequisites_closure(c["skill"]):
            if pre in owned or pre in cands:
                continue
            cands[pre] = {
                "skill": pre, "status": "missing", "priority": 0.6 * c["priority"],
                "reason": f"Foundation for {tax.name(c['skill'])}", "prerequisite_of": c["skill"],
            }
    return list(cands.values())


def _order(tax: SkillTaxonomy, cands: list[dict]) -> list[dict]:
    """Kahn's algorithm; among ready nodes always take the highest-priority one."""
    by_slug = {c["skill"]: c for c in cands}
    deps = {s: {p for p in tax.get(s)["prerequisites"] if p in by_slug} if tax.get(s) else set() for s in by_slug}
    done: set[str] = set()
    out: list[dict] = []
    while len(out) < len(by_slug):
        ready = [s for s in by_slug if s not in done and deps[s] <= done]
        if not ready:  # cycle guard (bad admin data) — fall back to priority order
            ready = [s for s in by_slug if s not in done]
        nxt = max(ready, key=lambda s: (by_slug[s]["priority"], s))
        done.add(nxt)
        out.append(by_slug[nxt])
    return out


def pick_course(courses_by_skill: dict[str, list[dict]], slug: str, status: str) -> dict | None:
    options = courses_by_skill.get(slug, [])
    if not options:
        return None
    want = "intermediate" if status == "partial" else "beginner"
    ranked = sorted(options, key=lambda c: (c.get("level") != want, not c.get("curated", False), not c.get("free", False), c.get("hours", 99)))
    c = ranked[0]
    return {"id": str(c["_id"]), "title": c["title"], "provider": c["provider"], "url": c["url"],
            "level": c["level"], "hours": c["hours"], "free": c.get("free", False), "curated": c.get("curated", False)}


def build_roadmap(tax: SkillTaxonomy, cands: list[dict], courses: list[dict], hours_per_week: int = 8,
                  project_idea: str | None = None, phase_weeks: int = 4) -> dict:
    hours_per_week = max(1, min(int(hours_per_week), 60))
    by_skill: dict[str, list[dict]] = {}
    for c in courses:
        for s in c.get("skill_ids", []):
            by_skill.setdefault(s, []).append(c)

    items = []
    for c in _order(tax, cands):
        skill = tax.get(c["skill"])
        course = pick_course(by_skill, c["skill"], c["status"])
        base = (course["hours"] if course else skill["hours"])
        hours = max(4, round(base * (0.6 if c["status"] == "partial" else 1.0)))
        items.append({
            "id": uuid.uuid4().hex[:12], "type": "skill", "skill_slug": c["skill"], "skill_name": skill["name"],
            "category": skill["category"], "reason": c["reason"], "status": c["status"],
            "est_hours": hours, "course": course, "completed": False, "completed_at": None,
        })

    if project_idea:
        items.append({
            "id": uuid.uuid4().hex[:12], "type": "project", "skill_slug": None, "skill_name": "Capstone project",
            "category": "Portfolio", "reason": project_idea, "status": "project", "est_hours": 20,
            "course": None, "completed": False, "completed_at": None,
        })

    capacity = hours_per_week * phase_weeks
    phases: list[dict] = []
    cur: list[dict] = []
    cur_h = 0
    for it in items:
        if cur and cur_h + it["est_hours"] > capacity * 1.25 and it["type"] != "project":
            phases.append({"items": cur, "hours": cur_h}); cur, cur_h = [], 0
        cur.append(it); cur_h += it["est_hours"]
    if cur:
        phases.append({"items": cur, "hours": cur_h})

    elapsed = 0.0
    for n, ph in enumerate(phases, 1):
        start_w = math.floor(elapsed / hours_per_week) + 1
        elapsed += ph["hours"]
        end_w = max(start_w, math.ceil(elapsed / hours_per_week))
        cats = [i["category"] for i in ph["items"] if i["type"] == "skill"]
        focus = max(set(cats), key=cats.count) if cats else "Portfolio"
        ph.update({"index": n, "title": f"Phase {n}", "weeks": f"Weeks {start_w}–{end_w}", "focus": focus})

    total = sum(p["hours"] for p in phases)
    return {"phases": phases, "total_hours": total, "estimated_weeks": math.ceil(total / hours_per_week) if total else 0,
            "hours_per_week": hours_per_week}


def compute_progress(phases: list[dict]) -> dict:
    items = [i for p in phases for i in p["items"]]
    total_h = sum(i["est_hours"] for i in items) or 1
    done = [i for i in items if i["completed"]]
    done_h = sum(i["est_hours"] for i in done)
    return {"progress_pct": round(100 * done_h / total_h, 1), "completed_hours": done_h,
            "completed_items": len(done), "total_items": len(items)}
