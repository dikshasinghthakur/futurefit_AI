"""Resume parsing: section detection, taxonomy-based skill extraction with confidence, and light
entity extraction (contact, education, certifications, experience years). Deterministic and offline;
an optional LLM pass (services/llm.py) can add skills on top."""
from __future__ import annotations

import re
from datetime import date

from app.services.taxonomy import SkillTaxonomy

_HEADINGS = {
    "skills": r"(?:technical\s+|key\s+|core\s+)?skills?(?:\s*(?:&|and)\s*(?:tools|technologies))?|core competenc(?:y|ies)|technologies|tech stack|tools(?:\s*(?:&|and)\s*technologies)?",
    "experience": r"(?:work\s+|professional\s+|relevant\s+)?experience|employment(?:\s+history)?|internships?|work history",
    "education": r"education(?:al)?(?:\s+(?:background|qualifications?))?|academics?|academic background",
    "projects": r"(?:academic\s+|personal\s+|key\s+)?projects?",
    "certifications": r"certifications?|licen[sc]es?(?:\s*(?:&|and)\s*certifications?)?|courses?|training",
    "summary": r"(?:professional\s+|career\s+)?(?:summary|objective)|profile|about me",
    "achievements": r"achievements?|awards?|honou?rs?|accomplishments?|extracurricular(?:s| activities)?",
}
_HEADING_RE = {k: re.compile(v, re.I) for k, v in _HEADINGS.items()}

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(\+?\d[\d\s\-().]{8,}\d)(?!\d)")
_GITHUB = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w.-]+", re.I)
_LINKEDIN = re.compile(r"(?:https?://)?(?:[\w]+\.)?linkedin\.com/in/[\w%-]+", re.I)

_MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
_RANGE = re.compile(
    rf"(?:({_MONTHS})[a-z]*\.?,?\s+)?((?:19|20)\d{{2}})\s*(?:-|–|—|to)\s*"
    rf"(?:(?:({_MONTHS})[a-z]*\.?,?\s+)?((?:19|20)\d{{2}})|(present|current|now|ongoing|till date))",
    re.I,
)
_YEARS_PHRASE = re.compile(r"(\d{1,2})\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+|industry\s+|work\s+)?experience", re.I)

_DEGREE_CI = re.compile(
    r"\b(b\.?\s?tech|m\.?\s?tech|b\.?\s?sc|m\.?\s?sc|bca|mca|mba|bachelor|master|ph\.?\s?d|diploma|post[- ]graduate|undergraduate)\b", re.I
)
_DEGREE_CS = re.compile(r"\b(B\.E\.?|M\.E\.?|B\.Eng|M\.Eng)\b")


def _match_heading(line: str) -> str | None:
    cleaned = line.strip().strip(":•-*#|_=").strip()
    if not cleaned or len(cleaned) > 45:
        return None
    for key, rx in _HEADING_RE.items():
        if rx.fullmatch(cleaned):
            return key
    return None


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for line in text.splitlines():
        key = _match_heading(line)
        if key:
            current = key
            sections.setdefault(key, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def _months(m: str | None) -> int:
    return (_MONTHS.split("|").index(m[:3].lower()) + 1) if m else 1


def estimate_experience_years(experience_text: str, full_text: str, today: date | None = None) -> float:
    today = today or date.today()
    best_phrase = max((int(x) for x in _YEARS_PHRASE.findall(full_text)), default=0)
    spans: list[tuple[float, float]] = []
    for m in _RANGE.finditer(experience_text):
        sm, sy, em, ey, ongoing = m.groups()
        start = int(sy) + (_months(sm) - 1) / 12
        end = (today.year + (today.month - 1) / 12) if ongoing else int(ey) + (_months(em) - 1) / 12 + (1 / 12 if em else 0)
        if end > start and end - start < 40:
            spans.append((start, end))
    spans.sort()
    merged: list[list[float]] = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    computed = sum(e - s for s, e in merged)
    return round(max(computed, float(best_phrase)), 1)


def _first(rx: re.Pattern, text: str) -> str | None:
    m = rx.search(text)
    return m.group(0) if m else None


def _bullets(section: str, limit: int) -> list[str]:
    lines = [re.sub(r"^[\s•\-*·▪●]+", "", ln).strip() for ln in section.splitlines()]
    return [ln for ln in lines if len(ln) > 3][:limit]


def parse_resume(text: str, taxonomy: SkillTaxonomy) -> dict:
    sections = split_sections(text)
    skills_text = sections.get("skills", "")
    applied_text = "\n".join(sections.get(k, "") for k in ("experience", "projects", "certifications"))

    all_mentions = taxonomy.find(text)
    in_skills = taxonomy.find(skills_text) if skills_text else {}
    in_applied = taxonomy.find(applied_text) if applied_text else {}

    skills = []
    for slug, count in all_mentions.items():
        s = taxonomy.get(slug)
        conf = 0.45
        conf += 0.25 if slug in in_skills else 0.0
        conf += 0.20 if slug in in_applied else 0.0
        conf += 0.05 * min(count, 3)
        skills.append({
            "slug": slug, "name": s["name"], "category": s["category"],
            "mentions": count, "confidence": round(min(conf, 1.0), 2),
            "evidence": [k for k, v in (("skills", in_skills), ("experience/projects", in_applied)) if slug in v] or ["body"],
            "source": "nlp",
        })
    skills.sort(key=lambda x: (-x["confidence"], x["name"]))

    education = [ln for ln in _bullets(sections.get("education", ""), 12) if _DEGREE_CI.search(ln) or _DEGREE_CS.search(ln)][:4]
    if not education:
        education = [ln.strip() for ln in text.splitlines() if _DEGREE_CI.search(ln) or _DEGREE_CS.search(ln)][:3]

    phone = _PHONE.search(sections.get("header", text[:600]))
    return {
        "contact": {
            "email": _first(_EMAIL, text),
            "phone": phone.group(1).strip() if phone else None,
            "github": _first(_GITHUB, text),
            "linkedin": _first(_LINKEDIN, text),
        },
        "sections_found": [k for k in sections if k != "header"],
        "skills": skills,
        "education": education,
        "certifications": _bullets(sections.get("certifications", ""), 8),
        "experience_years": estimate_experience_years(sections.get("experience", ""), text),
        "word_count": len(text.split()),
    }
