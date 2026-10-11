"""Skill taxonomy seed.

Each skill: slug, display name, category, default learning hours, aliases (matched in resumes),
prerequisites (learning order + 'implied knowledge') and related skills (partial-match credit).
An alias prefixed with "=" must match with exact case (used for words that are also common English).
"""


def _s(slug, name, cat, hours, aliases="", prereqs="", related=""):
    split = lambda v: [x.strip() for x in v.split(",") if x.strip()]
    return {
        "slug": slug, "name": name, "category": cat, "hours": hours,
        "aliases": split(aliases), "prerequisites": split(prereqs), "related": split(related),
    }


PL, FE, BE, DB = "Programming Languages", "Frontend", "Backend & APIs", "Databases"
ML, DO, CS, SE = "Data & AI", "DevOps & Cloud", "CS Fundamentals", "Security"
TP, SO = "Tools & Practices", "Soft Skills"

SKILLS = [
    # Programming languages
    _s("python", "Python", PL, 40, "python3, py", "", "r-programming"),
    _s("java", "Java", PL, 50, "core java, java se, jdk", "", "csharp, cpp"),
    _s("javascript", "JavaScript", PL, 40, "js, es6, es2015, ecmascript, vanilla js", "", "typescript"),
    _s("typescript", "TypeScript", PL, 25, "ts", "javascript", "javascript"),
    _s("cpp", "C++", PL, 50, "cpp, c plus plus", "", "java, csharp"),
    _s("csharp", "C#", PL, 45, "c sharp, csharp", "", "java"),
    _s("go", "Go (Golang)", PL, 35, "golang, go lang", "", "java"),
    _s("r-programming", "R Programming", PL, 30, "rstudio, r language", "", "python, statistics"),
    _s("sql", "SQL", PL, 25, "structured query language, t-sql, pl/sql, plsql", "", "postgresql, mysql"),
    _s("shell", "Shell Scripting", PL, 15, "bash, zsh, shell, bash scripting", "linux", "linux"),
    # Frontend
    _s("html", "HTML", FE, 10, "html5, semantic html", "", "css"),
    _s("css", "CSS", FE, 15, "css3, scss, sass, flexbox, css grid", "html", "tailwind"),
    _s("react", "React", FE, 40, "react.js, reactjs, react js, react hooks", "javascript, html, css", "vue, angular, nextjs"),
    _s("nextjs", "Next.js", FE, 25, "nextjs, next js", "react", "react"),
    _s("vue", "Vue.js", FE, 30, "vue, vuejs, vue js, nuxt", "javascript", "react, angular"),
    _s("angular", "Angular", FE, 40, "angularjs, angular.js", "typescript", "react, vue"),
    _s("tailwind", "Tailwind CSS", FE, 10, "tailwind, tailwindcss, bootstrap", "css", "css"),
    _s("redux", "Redux", FE, 12, "redux toolkit, zustand, context api", "react", "react"),
    _s("responsive", "Responsive Design", FE, 8, "responsive web design, mobile-first, media queries, responsive ui", "css", "css"),
    _s("figma", "Figma & UI/UX", FE, 12, "ui design, ux design, ui/ux, wireframing, prototyping, adobe xd", "", ""),
    # Backend
    _s("nodejs", "Node.js", BE, 30, "node, nodejs, node js", "javascript", "express"),
    _s("express", "Express.js", BE, 15, "=Express, expressjs, express js", "nodejs", "nodejs"),
    _s("fastapi", "FastAPI", BE, 18, "fast api", "python", "django, flask"),
    _s("django", "Django", BE, 35, "django rest framework, drf", "python", "flask, fastapi"),
    _s("flask", "Flask", BE, 18, "", "python", "django, fastapi"),
    _s("springboot", "Spring Boot", BE, 45, "springboot, spring framework, spring mvc, hibernate", "java", "java"),
    _s("rest", "REST APIs", BE, 15, "restful, rest api, restful api, rest apis, api design, web services, api development", "", "graphql"),
    _s("graphql", "GraphQL", BE, 15, "apollo graphql, apollo server", "rest", "rest"),
    _s("auth", "Auth & Security (JWT/OAuth)", BE, 12, "jwt, oauth, oauth2, authentication, authorization, rbac, role-based access control", "rest", "cybersecurity"),
    _s("microservices", "Microservices", BE, 30, "micro services, service-oriented architecture, soa", "rest", "system-design"),
    _s("system-design", "System Design", BE, 40, "scalability, distributed systems, high-level design, low-level design, hld, lld, system architecture", "rest, db-design", "microservices"),
    _s("message-queues", "Message Queues", BE, 15, "kafka, rabbitmq, celery, pub/sub, sqs", "", "microservices"),
    # Databases
    _s("mongodb", "MongoDB", DB, 20, "mongo, mongoose, nosql", "", "postgresql, mysql"),
    _s("postgresql", "PostgreSQL", DB, 20, "postgres, psql", "sql", "mysql, mongodb"),
    _s("mysql", "MySQL", DB, 15, "mariadb, oracle db, sql server", "sql", "postgresql"),
    _s("redis", "Redis", DB, 10, "caching, memcached, in-memory cache", "", ""),
    _s("db-design", "Database Design", DB, 20, "database normalization, schema design, dbms, erd, data modeling, data modelling, rdbms", "sql", "sql"),
    # Data & AI
    _s("numpy", "NumPy", ML, 10, "", "python", "pandas"),
    _s("pandas", "Pandas", ML, 15, "dataframes, data wrangling, data cleaning, data preprocessing", "python", "numpy"),
    _s("statistics", "Statistics", ML, 30, "statistical analysis, probability, hypothesis testing, a/b testing, regression analysis", "", "machine-learning"),
    _s("sklearn", "Scikit-learn", ML, 25, "sklearn, scikit learn", "python, statistics", "machine-learning"),
    _s("machine-learning", "Machine Learning", ML, 50, "ml, supervised learning, unsupervised learning, predictive modeling, predictive modelling, xgboost, random forest", "python, statistics", "sklearn, deep-learning"),
    _s("deep-learning", "Deep Learning", ML, 50, "neural networks, cnn, rnn, lstm, transformers, computer vision", "machine-learning", "tensorflow, pytorch"),
    _s("tensorflow", "TensorFlow", ML, 30, "keras", "deep-learning", "pytorch"),
    _s("pytorch", "PyTorch", ML, 30, "torch", "deep-learning", "tensorflow"),
    _s("nlp", "Natural Language Processing", ML, 40, "nlp, text mining, spacy, nltk, hugging face, huggingface, text classification", "machine-learning", "llm"),
    _s("llm", "LLMs & Prompt Engineering", ML, 20, "large language models, llm, llms, prompt engineering, openai api, langchain, rag, retrieval-augmented generation, generative ai, genai", "nlp", "nlp"),
    _s("data-viz", "Data Visualization", ML, 15, "matplotlib, seaborn, tableau, power bi, powerbi, chart.js, d3.js, plotly, dashboards", "", "pandas"),
    _s("mlops", "MLOps", ML, 25, "mlflow, model deployment, kubeflow, model serving", "machine-learning, docker", "docker"),
    _s("excel", "Microsoft Excel", ML, 10, "=Excel, ms excel, advanced excel, excel formulas, pivot tables, spreadsheets, google sheets", "", ""),
    # DevOps & cloud
    _s("git", "Git & GitHub", DO, 8, "git, github, gitlab, version control, bitbucket", "", ""),
    _s("linux", "Linux", DO, 20, "ubuntu, unix, linux administration, centos", "", "shell"),
    _s("docker", "Docker", DO, 15, "containers, containerization, dockerfile, docker compose", "linux", "kubernetes"),
    _s("kubernetes", "Kubernetes", DO, 35, "k8s, helm, container orchestration", "docker", "docker"),
    _s("ci-cd", "CI/CD", DO, 15, "github actions, jenkins, continuous integration, continuous delivery, continuous deployment, gitlab ci, circleci, devops pipelines", "git", "docker"),
    _s("aws", "AWS", DO, 40, "amazon web services, ec2, s3, aws lambda, cloudformation", "linux", "azure, gcp"),
    _s("azure", "Microsoft Azure", DO, 40, "azure", "", "aws, gcp"),
    _s("gcp", "Google Cloud", DO, 40, "gcp, google cloud platform, bigquery, firebase", "", "aws, azure"),
    _s("terraform", "Terraform & IaC", DO, 20, "infrastructure as code, iac, ansible, pulumi", "linux", "aws"),
    _s("monitoring", "Monitoring & Observability", DO, 15, "prometheus, grafana, elk stack, datadog, observability, application monitoring", "linux", ""),
    _s("networking", "Computer Networks", DO, 20, "computer networks, computer networking, tcp/ip, dns, load balancing, osi model, network protocols", "", "cybersecurity"),
    # CS fundamentals & practices
    _s("dsa", "Data Structures & Algorithms", CS, 60, "dsa, algorithms, data structures, competitive programming, leetcode, algorithmic problem solving", "", "problem-solving"),
    _s("oop", "Object-Oriented Programming", CS, 20, "oop, oops, object oriented, object-oriented design", "", "design-patterns"),
    _s("design-patterns", "Design Patterns", CS, 20, "solid principles, software design patterns, clean architecture, clean code", "oop", "oop"),
    _s("os", "Operating Systems", CS, 25, "os concepts, process scheduling, memory management, multithreading, concurrency", "", "linux"),
    _s("testing", "Software Testing", TP, 15, "unit testing, pytest, jest, junit, tdd, test-driven development, selenium, cypress, integration testing, postman, qa automation", "", ""),
    _s("agile", "Agile & Scrum", TP, 6, "scrum, kanban, jira, sprint planning, agile methodology", "", ""),
    # Security
    _s("cybersecurity", "Cybersecurity Fundamentals", SE, 30, "information security, infosec, cyber security, owasp, penetration testing, pentesting, ethical hacking, vulnerability assessment, kali linux", "networking, linux", "cryptography, siem"),
    _s("cryptography", "Cryptography", SE, 25, "encryption, pki, ssl/tls, hashing, public key infrastructure", "", "cybersecurity"),
    _s("siem", "SIEM & Incident Response", SE, 25, "splunk, incident response, soc, threat detection, wireshark, threat hunting", "cybersecurity", "cybersecurity"),
    # Soft skills
    _s("communication", "Communication", SO, 8, "communication skills, presentation skills, public speaking, technical writing, stakeholder management", "", "teamwork"),
    _s("teamwork", "Teamwork & Collaboration", SO, 6, "team player, collaboration, cross-functional, team collaboration", "", "communication"),
    _s("leadership", "Leadership", SO, 10, "team lead, mentoring, led a team, project management, team leadership", "", "communication"),
    _s("problem-solving", "Problem Solving", SO, 10, "analytical thinking, critical thinking, troubleshooting, analytical skills, debugging", "", "dsa"),
]
