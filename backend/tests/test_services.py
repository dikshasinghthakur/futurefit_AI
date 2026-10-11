from datetime import date

from app.data.roles import ROLES
from app.data.skills import SKILLS
from app.services.gap_analysis import analyze_gap
from app.services.roadmap import build_roadmap, compute_progress, plan_targets
from app.services.skill_extractor import estimate_experience_years, parse_resume, split_sections
from app.services.taxonomy import SkillTaxonomy

TAX = SkillTaxonomy(SKILLS)
ROLE = {r["slug"]: r for r in ROLES}

RESUME = """Diksha Sharma
diksha@example.com | +91 98765 43210 | github.com/diksha | linkedin.com/in/diksha

SUMMARY
Final-year B.Tech CSE student.

TECHNICAL SKILLS
Languages: Python, Java, JavaScript, C++, SQL
Web: React.js, HTML5, CSS3, Node.js, Express
Databases: MongoDB, MySQL
Tools: Git, GitHub, Docker, Postman, VS Code

PROJECTS
Smart Library - Built a REST API with Express and MongoDB, JWT auth, deployed using Docker.
Sentiment tool - NLP pipeline with scikit-learn and pandas.

EXPERIENCE
Web Development Intern, Acme - Jun 2025 - Aug 2025
Led a team of 3 students; strong communication and problem solving.

EDUCATION
B.Tech Computer Science and Engineering, Echelon Institute of Technology, 2023 - 2027

CERTIFICATIONS
- Machine Learning Specialization (Coursera)
"""


def slugs(parsed):
    return {s["slug"] for s in parsed["skills"]}


def test_extracts_skills_and_aliases():
    got = slugs(parse_resume(RESUME, TAX))
    for expect in ["python", "java", "javascript", "cpp", "sql", "react", "html", "css", "nodejs", "express",
                   "mongodb", "mysql", "git", "docker", "sklearn", "pandas", "nlp", "auth", "rest", "testing"]:
        assert expect in got, expect


def test_word_boundaries_prevent_false_positives():
    got = TAX.find("Used JavaScript and Three.js. Please go to the market; we excel in teamwork. Express interest.")
    assert "javascript" in got and "java" not in got
    assert "go" not in got and "excel" not in got and "express" not in got


def test_exact_case_alias_excel():
    assert "excel" in TAX.find("Skills: Excel, SQL")
    assert "excel" not in TAX.find("we excel at delivery")


def test_cpp_and_csharp_symbols():
    got = TAX.find("Proficient in C++, C# and Go (Golang).")
    assert {"cpp", "csharp", "go"} <= set(got)


def test_confidence_higher_when_in_skills_and_projects():
    parsed = parse_resume(RESUME, TAX)
    conf = {s["slug"]: s["confidence"] for s in parsed["skills"]}
    assert conf["mongodb"] > conf["communication"]


def test_sections_contact_education_and_experience():
    parsed = parse_resume(RESUME, TAX)
    assert {"skills", "projects", "experience", "education"} <= set(parsed["sections_found"])
    assert parsed["contact"]["email"] == "diksha@example.com"
    assert parsed["contact"]["github"].endswith("github.com/diksha")
    assert any("B.Tech" in e for e in parsed["education"])
    assert 0.1 <= parsed["experience_years"] <= 0.5  # three-month internship


def test_experience_years_merges_overlaps():
    txt = "Jan 2020 - Dec 2021\nJun 2021 - Present"
    yrs = estimate_experience_years(txt, txt, today=date(2024, 1, 1))
    assert 3.5 <= yrs <= 4.2


def test_split_sections_ignores_inline_words():
    s = split_sections("Name\nSKILLS\nPython\nEXPERIENCE\nBuilt things with skills and projects")
    assert s["skills"] == "Python" and "projects" not in s


def test_gap_analysis_statuses():
    parsed = parse_resume(RESUME, TAX)
    user = {s["slug"]: s["confidence"] for s in parsed["skills"]}
    res = analyze_gap(TAX, user, ROLE["fullstack-developer"])
    status = {i["skill"]: i for i in res["matched"] + res["partial"] + res["missing"]}
    assert status["react"]["status"] == "matched"
    assert status["typescript"]["status"] in ("partial", "missing")
    assert status["typescript"]["status"] == "partial"  # knows JavaScript -> related
    assert status["ci-cd"]["status"] in ("partial", "missing")  # Docker knowledge gives at most partial credit
    assert status["agile"]["status"] == "missing"
    assert 0 < res["readiness_score"] < 100
    assert res["counts"]["matched"] + res["counts"]["partial"] + res["counts"]["missing"] == len(ROLE["fullstack-developer"]["skills"])


def test_alternative_and_implied_credit():
    role = {"skills": [{"skill": "fastapi", "weight": 3, "alt": ["django"]}, {"skill": "javascript", "weight": 2, "alt": []}]}
    res = analyze_gap(TAX, {"django": 0.9, "react": 0.9}, role)
    by = {i["skill"]: i for i in res["matched"]}
    assert by["fastapi"]["via"] == "django"
    assert by["javascript"]["via"] == "react"  # React implies JavaScript


def test_empty_profile_scores_zero():
    res = analyze_gap(TAX, {}, ROLE["data-scientist"])
    assert res["readiness_score"] == 0 and res["counts"]["missing"] == len(ROLE["data-scientist"]["skills"])


def test_all_roles_reference_valid_skills():
    for r in ROLES:
        for s in r["skills"]:
            assert s["skill"] in TAX.skills, (r["slug"], s["skill"])
            assert all(a in TAX.skills for a in s["alt"]), (r["slug"], s["alt"])
    for s in SKILLS:
        for ref in s["prerequisites"] + s["related"]:
            assert ref in TAX.skills, (s["slug"], ref)


def test_roadmap_respects_prerequisite_order_and_phases():
    user = {"python": 0.9, "html": 0.8}
    res = analyze_gap(TAX, user, ROLE["ml-engineer"])
    cands = plan_targets(TAX, res, owned=set(user))
    fake_courses = [{"_id": "c1", "title": "ML 101", "provider": "X", "url": "https://x", "level": "beginner",
                     "hours": 30, "free": True, "curated": True, "skill_ids": ["machine-learning"]}]
    rm = build_roadmap(TAX, cands, fake_courses, hours_per_week=10, project_idea="Build X")
    order = [i["skill_slug"] for p in rm["phases"] for i in p["items"] if i["type"] == "skill"]
    for slug in order:
        for pre in TAX.get(slug)["prerequisites"]:
            if pre in order:
                assert order.index(pre) < order.index(slug), (pre, slug)
    assert rm["phases"][-1]["items"][-1]["type"] == "project"
    assert rm["total_hours"] == sum(p["hours"] for p in rm["phases"]) and rm["estimated_weeks"] >= 1
    assert "statistics" in order and order.index("statistics") < order.index("machine-learning")  # prereq auto-added


def test_progress_calculation():
    user = {"python": 0.9}
    res = analyze_gap(TAX, user, ROLE["data-analyst"])
    rm = build_roadmap(TAX, plan_targets(TAX, res, {"python"}), [], 6)
    rm["phases"][0]["items"][0]["completed"] = True
    p = compute_progress(rm["phases"])
    assert p["completed_items"] == 1 and 0 < p["progress_pct"] < 100
