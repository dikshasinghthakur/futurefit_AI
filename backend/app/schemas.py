from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshIn(BaseModel):
    refresh_token: str


class ProfileIn(BaseModel):
    headline: str | None = Field(default=None, max_length=120)
    education: str | None = Field(default=None, max_length=160)
    graduation_year: int | None = Field(default=None, ge=1990, le=2100)
    location: str | None = Field(default=None, max_length=80)
    career_goal: str | None = Field(default=None, max_length=500)
    target_role_slug: str | None = Field(default=None, max_length=80)


class ResumeTextIn(BaseModel):
    text: str = Field(min_length=40, max_length=60_000)
    title: str = Field(default="Pasted resume", max_length=120)


class AnalysisIn(BaseModel):
    resume_id: str
    role_slug: str


class RoadmapIn(BaseModel):
    analysis_id: str
    hours_per_week: int = Field(default=8, ge=1, le=60)


class ItemToggleIn(BaseModel):
    completed: bool


# ---- admin ----
class RoleSkillIn(BaseModel):
    skill: str
    weight: int = Field(ge=1, le=5)
    alt: list[str] = []


class RoleUpsert(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=400)
    project_idea: str = Field(default="", max_length=400)
    skills: list[RoleSkillIn] = Field(min_length=1, max_length=60)


class SkillUpsert(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=60)
    name: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=2, max_length=60)
    hours: int = Field(default=20, ge=1, le=300)
    aliases: list[str] = []
    prerequisites: list[str] = []
    related: list[str] = []


class CourseUpsert(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    provider: str = Field(min_length=2, max_length=80)
    url: str = Field(pattern=r"^https?://", max_length=500)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    hours: int = Field(default=10, ge=1, le=500)
    free: bool = True
    skill_ids: list[str] = Field(min_length=1)
