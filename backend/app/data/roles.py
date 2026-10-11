"""Target role seed. Compact spec: 'skill:weight[:alt1|alt2]' — weight 1 (nice to have) .. 5 (essential).
`alt` skills count as an equivalent (e.g. Django satisfies a FastAPI requirement)."""


def _role(slug, title, description, project, spec):
    skills = []
    for token in spec.split():
        parts = token.split(":")
        skills.append({
            "skill": parts[0],
            "weight": int(parts[1]),
            "alt": parts[2].split("|") if len(parts) > 2 else [],
        })
    return {"slug": slug, "title": title, "description": description, "project_idea": project, "skills": skills}


ROLES = [
    _role("fullstack-developer", "Full Stack Developer",
          "Builds complete web products: responsive interfaces, APIs, databases and deployment.",
          "Ship a full-stack app (auth, CRUD, charts) with a React frontend, REST API, database and a Docker deployment.",
          "html:4 css:4 javascript:5 typescript:3 react:5:vue|angular nodejs:4:fastapi|django|flask|springboot express:3:fastapi|django|flask "
          "rest:5 mongodb:3:postgresql|mysql sql:3:postgresql|mysql|mongodb db-design:3 auth:3 git:4 docker:3 testing:3 ci-cd:2 "
          "dsa:3 responsive:3 agile:2 communication:2 problem-solving:3"),
    _role("frontend-developer", "Frontend Developer",
          "Crafts fast, accessible and polished user interfaces with modern frameworks.",
          "Rebuild a real product's landing page and dashboard with animations, a design system and Lighthouse score above 90.",
          "html:5 css:5 javascript:5 typescript:4 react:5:vue|angular nextjs:3 tailwind:3:css responsive:4 redux:2 figma:2 "
          "testing:3 git:4 rest:3 dsa:2 communication:2 teamwork:2 problem-solving:2"),
    _role("backend-developer", "Backend Developer",
          "Designs reliable, scalable services, APIs and data models.",
          "Build a rate-limited, authenticated REST API with caching, background jobs, tests and CI/CD.",
          "python:4:java|go|nodejs fastapi:4:django|flask|springboot|express rest:5 sql:4:postgresql|mysql postgresql:3:mysql mongodb:3 "
          "redis:3 db-design:4 auth:4 docker:4 ci-cd:3 git:4 testing:4 system-design:4 microservices:3 message-queues:2 "
          "linux:3 aws:3:azure|gcp dsa:3 communication:2"),
    _role("data-scientist", "Data Scientist",
          "Turns data into models and decisions with statistics and machine learning.",
          "End-to-end ML project: clean a messy dataset, train and compare models, and deploy a prediction API with a dashboard.",
          "python:5 sql:4 pandas:5 numpy:4 statistics:5 machine-learning:5 sklearn:4 deep-learning:3 data-viz:4 nlp:2 "
          "git:3 mlops:2 communication:3 problem-solving:3 excel:1"),
    _role("ml-engineer", "Machine Learning Engineer",
          "Productionises models: training pipelines, serving, monitoring and scale.",
          "Train a model, wrap it in a FastAPI service, containerise it, add experiment tracking and CI.",
          "python:5 machine-learning:5 deep-learning:4 pytorch:4:tensorflow sklearn:3 numpy:3 pandas:4 statistics:3 mlops:4 docker:4 "
          "git:4 aws:3:azure|gcp ci-cd:3 linux:3 dsa:3 system-design:2 nlp:2 llm:2 testing:3"),
    _role("data-analyst", "Data Analyst",
          "Finds insights in data and communicates them through dashboards and stories.",
          "Analyse a public dataset, build an interactive dashboard and write up three decision-ready insights.",
          "sql:5 excel:4 data-viz:5 statistics:4 python:3:r-programming pandas:4 communication:4 problem-solving:3 db-design:2 agile:1"),
    _role("devops-engineer", "DevOps Engineer",
          "Automates delivery and keeps systems reliable, observable and secure.",
          "Automate a CI/CD pipeline that builds, tests and deploys a containerised app to Kubernetes with monitoring.",
          "linux:5 shell:4 git:4 docker:5 kubernetes:4 ci-cd:5 aws:4:azure|gcp terraform:4 monitoring:4 networking:3 python:2:go|shell "
          "cybersecurity:2 communication:2 problem-solving:3"),
    _role("cybersecurity-analyst", "Cybersecurity Analyst",
          "Detects, investigates and prevents threats across systems and networks.",
          "Set up a home lab, run a vulnerability assessment, and write an incident-response report with remediation steps.",
          "cybersecurity:5 networking:5 linux:4 cryptography:3 siem:4 python:2:shell auth:2 os:3 communication:3 problem-solving:3 shell:2"),
    _role("software-engineer", "Software Engineer (Campus / Generalist)",
          "Strong fundamentals across algorithms, systems and clean software engineering.",
          "Build and open-source a non-trivial project with tests, docs and CI, and solve 150+ DSA problems.",
          "dsa:5 oop:4 java:4:cpp|python|csharp|go sql:3 db-design:3 os:3 networking:2 git:4 testing:3 design-patterns:3 "
          "system-design:2 rest:3 agile:2 communication:3 teamwork:3 problem-solving:4"),
]
