"""In-memory skill taxonomy: alias matching (regex) + similarity matrix (TF-IDF char n-grams).
Pure Python/NumPy/scikit-learn — no web or DB imports, so it is trivially unit-testable."""
from __future__ import annotations

import re
from functools import cached_property

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_WS = re.compile(r"\s+")
# A skill mention must not be glued to other word characters (so "Java" never matches inside "JavaScript",
# and "Three.js" never yields a bare "js"); a trailing sentence period is fine.
_LB = r"(?<![A-Za-z0-9_+#.])"
_LA = r"(?![A-Za-z0-9_+#]|\.[A-Za-z0-9])"


def normalize(text: str) -> str:
    return _WS.sub(" ", text.lower().strip())


def _variants(alias: str) -> set[str]:
    a = normalize(alias)
    return {a, a.replace("-", " "), a.replace(" ", "-")}


class SkillTaxonomy:
    def __init__(self, skills: list[dict]):
        self.skills: dict[str, dict] = {s["slug"]: s for s in skills}
        self.slugs = list(self.skills)
        self._idx = {s: i for i, s in enumerate(self.slugs)}
        self._build_patterns()

    # ---------- lookup ----------
    def get(self, slug: str) -> dict | None:
        return self.skills.get(slug)

    def name(self, slug: str) -> str:
        s = self.skills.get(slug)
        return s["name"] if s else slug

    def category(self, slug: str) -> str:
        s = self.skills.get(slug)
        return s["category"] if s else "Other"

    # ---------- text matching ----------
    def _build_patterns(self) -> None:
        alias_map: dict[str, str] = {}
        exact_map: dict[str, str] = {}
        for s in self.skills.values():
            for raw in [s["name"], *s.get("aliases", [])]:  # slugs are NOT aliases ("go", "excel", "express" are English words)
                if raw.startswith("="):
                    exact_map[raw[1:]] = s["slug"]
                    continue
                for v in _variants(raw):
                    alias_map.setdefault(v, s["slug"])
        self._alias_map = alias_map
        self._exact_map = exact_map
        alts = sorted(alias_map, key=len, reverse=True)  # longest first => "react native" beats "react"
        self._pattern = re.compile(_LB + "(" + "|".join(re.escape(a) for a in alts) + ")" + _LA, re.I) if alts else None
        # Exact-case aliases are also English words ("Excel", "Express"): require capitalisation AND list context
        # (followed by a delimiter / end of line), e.g. "Tools: Excel, SQL" but not "we excel at" / "Express interest".
        self._exact_pattern = (
            re.compile(_LB + "(" + "|".join(re.escape(a) for a in exact_map) + r")(?=[ \t]*(?:[,|/;•)\]]|\r?$))", re.M)
            if exact_map else None
        )

    def find(self, text: str) -> dict[str, int]:
        """slug -> number of mentions in `text`."""
        flat = _WS.sub(" ", text)
        counts: dict[str, int] = {}
        if self._pattern:
            for m in self._pattern.finditer(flat):
                slug = self._alias_map.get(normalize(m.group(1)))
                if slug:
                    counts[slug] = counts.get(slug, 0) + 1
        if self._exact_pattern:
            for m in self._exact_pattern.finditer(text):
                slug = self._exact_map[m.group(1)]
                counts[slug] = counts.get(slug, 0) + 1
        return counts

    def resolve(self, name_or_slug: str) -> str | None:
        key = normalize(name_or_slug)
        if name_or_slug in self.skills:
            return name_or_slug
        return self._alias_map.get(key) or self._alias_map.get(key.replace(" ", "-"))

    # ---------- graph ----------
    def prerequisites_closure(self, slug: str) -> set[str]:
        seen: set[str] = set()
        stack = list(self.skills.get(slug, {}).get("prerequisites", []))
        while stack:
            p = stack.pop()
            if p in seen or p not in self.skills:
                continue
            seen.add(p)
            stack.extend(self.skills[p].get("prerequisites", []))
        return seen

    # ---------- similarity ----------
    @cached_property
    def _tfidf_sim(self) -> np.ndarray:
        docs = [" ".join([s["name"], *[a.lstrip("=") for a in s.get("aliases", [])]]).lower() for s in self.skills.values()]
        if len(docs) < 2:
            return np.eye(len(docs))
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)
        x = vec.fit_transform(docs)  # rows are L2-normalised -> dot product == cosine similarity
        return (x @ x.T).toarray()

    def relatedness(self, have: str, need: str) -> float:
        """How much does knowing `have` help with `need`? 0..1 (structure-based)."""
        h, n = self.skills.get(have), self.skills.get(need)
        if not h or not n:
            return 0.0
        if need in h.get("related", []) or have in n.get("related", []):
            return 0.85
        if have in n.get("prerequisites", []):
            return 0.7  # knows the foundation of the missing skill
        if h["category"] == n["category"]:
            return 0.2
        return 0.0

    def similarity(self, have: str, need: str) -> float:
        if have not in self._idx or need not in self._idx:
            return 0.0
        cos = float(self._tfidf_sim[self._idx[have], self._idx[need]])
        return 0.5 * cos + 0.5 * self.relatedness(have, need)
