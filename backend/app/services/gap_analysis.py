"""Skill-gap engine. For every skill a role requires, decide matched / partial / missing and score it.

matched  : user has the skill (score 0.8-1.0, scaled by extraction confidence), OR has an accepted alternative
           (e.g. Django for FastAPI), OR a more advanced skill that implies it (React implies JavaScript).
partial  : user has related knowledge (TF-IDF name similarity + curated relatedness) -> capped credit of 0.55.
missing  : nothing relevant -> 0.
Readiness = weighted coverage, weights being the role's importance (1-5) of each skill.
"""
from __future__ import annotations

from app.services.taxonomy import SkillTaxonomy

PARTIAL_THRESHOLD = 0.40
PARTIAL_CAP = 0.55
ALT_CREDIT = 0.85
IMPLIED_CREDIT = 0.80


def readiness_label(score: float) -> str:
    if score < 35:
        return "Getting started"
    if score < 60:
        return "Building momentum"
    if score < 80:
        return "Nearly there"
    return "Interview-ready"


def analyze_gap(tax: SkillTaxonomy, user_skills: dict[str, float], role: dict) -> dict:
    """user_skills: slug -> confidence (0..1). role: {'skills': [{'skill','weight','alt'}]}."""
    implied: dict[str, str] = {}  # prerequisite slug -> advanced skill that implies it
    for have in user_skills:
        for pre in tax.prerequisites_closure(have):
            implied.setdefault(pre, have)

    items = []
    for req in role["skills"]:
        slug, weight, alts = req["skill"], int(req["weight"]), req.get("alt", [])
        via, score, status = None, 0.0, "missing"

        if slug in user_skills:
            status, score = "matched", round(0.8 + 0.2 * user_skills[slug], 3)
        elif (owned_alt := next((a for a in alts if a in user_skills), None)):
            status, score, via = "matched", ALT_CREDIT, owned_alt
        elif slug in implied:
            status, score, via = "matched", IMPLIED_CREDIT, implied[slug]
        else:
            best, best_slug = 0.0, None
            for have in user_skills:
                for target in [slug, *alts]:
                    sim = tax.similarity(have, target)
                    if sim > best:
                        best, best_slug = sim, have
            if best >= PARTIAL_THRESHOLD:
                status, score, via = "partial", round(min(PARTIAL_CAP, best), 3), best_slug

        items.append({
            "skill": slug, "name": tax.name(slug), "category": tax.category(slug), "weight": weight,
            "status": status, "score": score, "via": via, "via_name": tax.name(via) if via else None,
            "alternatives": [tax.name(a) for a in alts],
        })

    total_w = sum(i["weight"] for i in items) or 1
    readiness = round(100 * sum(i["weight"] * i["score"] for i in items) / total_w, 1)

    by_cat: dict[str, dict] = {}
    for i in items:
        c = by_cat.setdefault(i["category"], {"weight": 0, "earned": 0.0, "skills": 0})
        c["weight"] += i["weight"]; c["earned"] += i["weight"] * i["score"]; c["skills"] += 1
    breakdown = {k: {"score": round(100 * v["earned"] / v["weight"], 1), "skills": v["skills"]} for k, v in by_cat.items()}

    groups = {s: [i for i in items if i["status"] == s] for s in ("matched", "partial", "missing")}
    for g in groups.values():
        g.sort(key=lambda i: (-i["weight"], i["name"]))
    top_gaps = sorted(groups["missing"] + groups["partial"], key=lambda i: (-i["weight"] * (1 - i["score"]), i["name"]))[:5]

    n_total = len(items)
    summary = f"You already cover {len(groups['matched'])} of {n_total} skills this role asks for."
    if top_gaps:
        summary += " Biggest opportunities: " + ", ".join(g["name"] for g in top_gaps[:3]) + "."
    else:
        summary += " No gaps found — focus on projects and interview practice."

    return {
        "readiness_score": readiness,
        "readiness_label": readiness_label(readiness),
        "counts": {k: len(v) for k, v in groups.items()},
        "matched": groups["matched"], "partial": groups["partial"], "missing": groups["missing"],
        "top_gaps": [g["skill"] for g in top_gaps],
        "category_breakdown": breakdown,
        "summary": summary,
    }
