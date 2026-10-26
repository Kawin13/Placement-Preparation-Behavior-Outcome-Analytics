"""
Database Seeder for Full Curriculum Across All Career Paths:
- Full-Stack Web Developer (FULLSTACK)
- AI & Machine Learning Engineer (AIML)
- Data Analyst & Business Intelligence (DATA_ANALYST)
- Software Development Engineer (SDE) - ensures complete synchronization
"""

from app.core.database import SessionLocal
from app.models.roadmap import (
    CareerPath,
    RoadmapSubject,
    RoadmapTopic,
    RoadmapSubtopic,
    LearningResource,
)
from app.models.dsa import DSATopic
from app.models.skill import Skill


def seed_all_curricula():
    db = SessionLocal()
    try:
        print("Starting comprehensive curriculum seeding across all career paths...")

        # 1. Fetch or create Career Paths
        paths_spec = [
            {
                "code": "SDE",
                "title": "Software Development Engineer (SDE)",
                "description": "Comprehensive interview curriculum covering algorithms, system structures, computer science fundamentals, and quantitative drills.",
                "target_role": "Software Development Engineer",
                "display_order": 1,
            },
            {
                "code": "FULLSTACK",
                "title": "Full-Stack Web Developer",
                "description": "Full-stack web engineering pathway focusing on frontend, backend APIs, relational databases, distributed state, and modern software design.",
                "target_role": "Full-Stack Developer",
                "display_order": 2,
            },
            {
                "code": "AIML",
                "title": "AI & Machine Learning Engineer",
                "description": "Applied intelligence track emphasizing mathematical foundations, data processing pipelines, neural architectures, and LLM integrations.",
                "target_role": "AI/ML Engineer",
                "display_order": 3,
            },
            {
                "code": "DATA_ANALYST",
                "title": "Data Analyst & Business Intelligence",
                "description": "Analytical pathway covering SQL queries, statistical reasoning, data modeling, visualization dashboards, and metric analysis.",
                "target_role": "Data Analyst",
                "display_order": 4,
            },
        ]

        paths_by_code = {}
        for p_spec in paths_spec:
            cp = db.query(CareerPath).filter(CareerPath.code == p_spec["code"]).first()
            if not cp:
                cp = CareerPath(**p_spec)
                db.add(cp)
                db.flush()
                print(f"Created Career Path: {cp.title}")
            else:
                cp.title = p_spec["title"]
                cp.description = p_spec["description"]
                cp.target_role = p_spec["target_role"]
                cp.display_order = p_spec["display_order"]
                cp.is_active = True
                db.flush()
            paths_by_code[p_spec["code"]] = cp

        # Cache DSA Topics & Skills
        dsa_topics = {t.slug: t.id for t in db.query(DSATopic).all()}
        skills = {s.name: s.id for s in db.query(Skill).all()}
        skill_domains = {s.domain: s.id for s in db.query(Skill).all()}

        # -------------------------------------------------------------
        # 2. FULLSTACK Curriculum
        # -------------------------------------------------------------
        fullstack_path = paths_by_code["FULLSTACK"]

        fullstack_subjects = [
            {
                "code": "FS-FRONTEND",
                "name": "Modern Frontend Engineering",
                "description": "HTML5 semantic structure, modern CSS flexbox & grid, ECMAScript standards, asynchronous DOM, and React component state architecture.",
                "icon": "Layout",
                "display_order": 1,
                "topics": [
                    {
                        "slug": "fs-html-dom",
                        "name": "HTML5 Semantic Architecture & DOM APIs",
                        "description": "Semantic markup, document object model traversal, event bubbling & capturing, and accessibility standards (WCAG).",
                        "learning_objectives": "Master document node manipulation, bubbling phase propagation, event delegation, and accessible semantic structuring.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 60,
                        "display_order": 1,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Semantic HTML & Accessibility", "description": "Header, main, section, nav, article landmarks and aria attributes."},
                            {"name": "DOM Tree Traversal & Manipulation", "description": "querySelector, createElement, fragment updates, and repaint/reflow optimization."},
                            {"name": "Event Delegation & Bubbling", "description": "Capturing vs bubbling phases, stopPropagation, and scalable list event handling."}
                        ],
                        "resources": [
                            {
                                "title": "Comprehensive Guide to DOM Manipulation & Event Bubbling",
                                "description": "Deep dive into browser rendering trees, event phases, and performance optimization when mutating DOM nodes.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": """# Modern HTML5 Semantic Architecture & DOM APIs

## 1. Browser Rendering Pipeline
When a web browser requests an HTML document, it follows a deterministic sequence:
1. **DOM Construction**: HTML parser converts raw bytes into characters, tokens, and nodes to build the DOM tree.
2. **CSSOM Construction**: CSS rules are parsed into the CSS Object Model.
3. **Render Tree**: Combining DOM and CSSOM to create visual render objects.
4. **Layout (Reflow)**: Calculating exact pixel coordinates and geometries.
5. **Paint**: Filling in raster pixels, layers, and composition.

```javascript
// Efficient DOM update using DocumentFragment to avoid multiple reflows
const fragment = document.createDocumentFragment();
data.forEach(item => {
  const el = document.createElement('div');
  el.className = 'candidate-row';
  el.textContent = item.name;
  fragment.appendChild(el);
});
document.getElementById('container').appendChild(fragment);
```

## 2. Event Bubbling & Delegation Pattern
Events in the DOM flow down during the **Capturing Phase** and bubble up during the **Bubbling Phase**.
Instead of attaching 1,000 listeners to table rows, attach a single listener to the parent table.

```javascript
document.querySelector('#student-table').addEventListener('click', (event) => {
  const targetBtn = event.target.closest('button[data-action]');
  if (!targetBtn) return;
  const action = targetBtn.dataset.action;
  console.log(`Executing ${action} for student:`, targetBtn.dataset.studentId);
});
```
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-css-grid",
                        "name": "Advanced CSS3, Flexbox & Responsive Layouts",
                        "description": "Multi-dimensional CSS Grid layouts, Flexbox alignment algorithms, CSS custom properties, media queries, and mobile-first responsive mechanics.",
                        "learning_objectives": "Construct responsive dashboards without frameworks using CSS Grid, flexbox axis invariants, and fluid clamp() typography.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 75,
                        "display_order": 2,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "CSS Flexbox Axis Alignment", "description": "justify-content, align-items, flex-grow, flex-shrink, and baseline offsets."},
                            {"name": "CSS Grid Template Areas", "description": "grid-template-columns, minmax, auto-fit vs auto-fill, and named grid areas."},
                            {"name": "Modern CSS Variables & Fluid Design", "description": "CSS custom properties, clamp(), calc(), and theme token switches."}
                        ],
                        "resources": [
                            {
                                "title": "Mastering Flexbox and CSS Grid for Engineering Dashboards",
                                "description": "Complete reference on 1D vs 2D layout systems, minmax responsiveness, and subgrid.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# CSS Flexbox & Grid Architecture

## 1. When to Use Flexbox vs CSS Grid
- **Flexbox**: 1-Dimensional layouts (either rows OR columns). Ideal for toolbars, badges, navigation menus, and form inputs.
- **CSS Grid**: 2-Dimensional layouts (rows AND columns simultaneously). Essential for complete page layouts, card galleries, and complex data panels.

## 2. Fluid Responsive Grid Example
```css
.portal-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  align-items: stretch;
}
```
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-js-async",
                        "name": "Modern JavaScript, Event Loop & Async/Await",
                        "description": "ECMAScript 2024 specifications, closures, call stack vs task queue, microtasks vs macrotasks, and Promise chaining invariants.",
                        "learning_objectives": "Predict event loop task ordering, author robust asynchronous code with async/await, and handle concurrent promises safely.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 90,
                        "display_order": 3,
                        "skill_id": skills.get("Arrays & Strings") or skill_domains.get("PROGRAMMING"),
                        "dsa_topic_id": dsa_topics.get("fundamentals-complexity"),
                        "subtopics": [
                            {"name": "Closures & Lexical Scope", "description": "Variable shadowing, closure memory lifecycle, and factory functions."},
                            {"name": "Event Loop & Microtask Queue", "description": "Call stack, Web APIs, Microtasks (Promises), and Macrotasks (setTimeout)."},
                            {"name": "Promise Combinators", "description": "Promise.all, Promise.allSettled, Promise.race, and Promise.any."}
                        ],
                        "resources": [
                            {
                                "title": "The JavaScript Event Loop & Concurrency Model",
                                "description": "Demystifying microtasks, macrotasks, async/await desugaring, and garbage collection.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# The JavaScript Event Loop & Asynchronous Mechanics

## 1. Execution Order Invariants
1. Synchronous code executes on the **Call Stack**.
2. Asynchronous operations register callbacks in Web APIs.
3. Microtasks (`Promise.then`, `queueMicrotask`, `process.nextTick`) are processed immediately after current call stack empties and **BEFORE** rendering.
4. Macrotasks (`setTimeout`, `setInterval`, I/O) are picked one at a time between rendering frames.

```javascript
console.log('1: Sync');
setTimeout(() => console.log('2: Macrotask'), 0);
Promise.resolve().then(() => console.log('3: Microtask'));
console.log('4: Sync End');

// Output order: 1, 4, 3, 2
```
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-react-hooks",
                        "name": "React Architecture: Components, Hooks & Virtual DOM",
                        "description": "Declarative UI rendering, virtual DOM reconciliation, useEffect synchronization rules, custom hooks, and memoization patterns.",
                        "learning_objectives": "Eliminate redundant React re-renders using useMemo/useCallback, design clean reusable hooks, and understand reconciliation fibers.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 100,
                        "display_order": 4,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Fiber Architecture & Reconciliation", "description": "Keys, diffing algorithm, commit vs render phases, and batched updates."},
                            {"name": "Hooks Invariants & Custom Hooks", "description": "useState, useEffect lifecycle, useRef DOM access, and custom abstraction hooks."},
                            {"name": "Performance Memoization", "description": "React.memo, useMemo, useCallback, and preventing prop reference thrashing."}
                        ],
                        "resources": [
                            {
                                "title": "Production React: State Management and Reconciliation",
                                "description": "Complete breakdown of React 18 concurrency, fiber reconciliation, and state isolation.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# Production React Architecture

## 1. Reconciliation & The Key Prop
React uses a heuristic O(n) diffing algorithm. Two elements of different types produce different trees. Keys must be stable, unique, and predictable.
Never use array indices as keys if items can be sorted, deleted, or inserted!

```tsx
// Custom hook for resilient data fetching
export function useFetchData<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isSubscribed = true;
    fetch(url)
      .then(res => res.json())
      .then(resData => { if (isSubscribed) { setData(resData); setLoading(false); } })
      .catch(err => { if (isSubscribed) { setError(err.message); setLoading(false); } });
    return () => { isSubscribed = false; };
  }, [url]);

  return { data, loading, error };
}
```
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "FS-BACKEND",
                "name": "Backend Architecture & REST APIs",
                "description": "Server-side web engineering, HTTP status codes, RESTful routing, authentication paradigms, middleware pipelines, and API validation.",
                "icon": "Server",
                "display_order": 2,
                "topics": [
                    {
                        "slug": "fs-rest-design",
                        "name": "RESTful API Standards & HTTP Protocol Invariants",
                        "description": "Idempotent HTTP methods (GET, PUT, DELETE), response status codes (2xx, 3xx, 4xx, 5xx), pagination headers, and REST resource naming.",
                        "learning_objectives": "Design enterprise-grade REST APIs with deterministic error schemas, cursor-based pagination, and correct HTTP verbs.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 60,
                        "display_order": 1,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "HTTP Verbs & Idempotence", "description": "Safety vs idempotency: GET, POST, PUT, PATCH, DELETE invariants."},
                            {"name": "Status Codes & Error Payloads", "description": "400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict."},
                            {"name": "Cursor & Offset Pagination", "description": "Limit/offset vs keyset pagination performance on large tables."}
                        ],
                        "resources": [
                            {
                                "title": "RESTful API Architecture & Industry Best Practices",
                                "description": "Designing clean, scalable REST endpoints with idempotency keys and structured JSON payloads.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": """# RESTful API Standards

## 1. HTTP Methods and Idempotence
An HTTP method is **idempotent** if producing multiple identical requests has the same intended effect on the server as a single request.
- `GET`: Safe & Idempotent
- `PUT`: Idempotent (replaces entire resource)
- `DELETE`: Idempotent (deleting once or 10 times results in resource being absent)
- `POST`: NOT idempotent (submitting twice creates two resources)
- `PATCH`: Generally NOT idempotent (e.g. increment operations)
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-server-arch",
                        "name": "Node.js & Python FastAPI Frameworks",
                        "description": "Asynchronous backend runtimes, request-response lifecycles, dependency injection, middleware chains, and input schema validation.",
                        "learning_objectives": "Build production backend services using FastAPI/Express with Pydantic validation and structured middleware.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 80,
                        "display_order": 2,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Middleware Pipelines", "description": "Logging, CORS headers, rate limiting, and exception interception."},
                            {"name": "Dependency Injection", "description": "Database session scoping and service decoupling."},
                            {"name": "Schema Validation", "description": "Pydantic & Zod input sanitation and type coercion."}
                        ],
                        "resources": [
                            {
                                "title": "High-Performance Backend Engineering with FastAPI and Express",
                                "description": "Async request pipelines, dependency injection, and non-blocking I/O handling.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# Modern Backend Server Architecture

## 1. Middleware Chain Pattern
Every request enters a pipeline of middlewares before reaching the route controller.
```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-auth-security",
                        "name": "Authentication, JWT, OAuth2 & Security",
                        "description": "Stateful vs stateless auth, JSON Web Token cryptography, refresh token rotation, password hashing (bcrypt/argon2), and CORS/CSRF protection.",
                        "learning_objectives": "Implement tamper-proof JWT authentication, role-based access control (RBAC), and secure cookie storage.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 90,
                        "display_order": 3,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Password Hashing & Salting", "description": "Why SHA256 is insecure for passwords; Argon2id and bcrypt work factors."},
                            {"name": "JWT Token Lifecycles", "description": "Access tokens (short-lived) vs refresh tokens (secure HTTP-only cookies)."},
                            {"name": "OWASP Web Security", "description": "Cross-Site Scripting (XSS), SQL Injection, and Cross-Site Request Forgery (CSRF)."}
                        ],
                        "resources": [
                            {
                                "title": "Enterprise Authentication: JWT, RBAC, and Web Security Defenses",
                                "description": "Securing web services against the OWASP Top 10 vulnerabilities.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# Enterprise Authentication & Security Architecture

## 1. Modern JWT Strategy
Never store access tokens in `localStorage` if sensitive, as any XSS vulnerability can exfiltrate tokens.
Use short-lived access tokens (15 minutes) kept in memory, paired with a refresh token stored in an `HttpOnly`, `SameSite=Strict`, `Secure` cookie.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "FS-DATABASE",
                "name": "Databases, ORM & Caching",
                "description": "Relational data modeling, schema normalization (3NF), B-Tree indexing, transaction isolation levels, and Redis caching.",
                "icon": "Database",
                "display_order": 3,
                "topics": [
                    {
                        "slug": "fs-relational-db",
                        "name": "Relational Modeling, Indexing & PostgreSQL",
                        "description": "Entity relationship diagrams, foreign key cascades, B-Tree vs Hash indexes, EXPLAIN ANALYZE query plans, and query optimization.",
                        "learning_objectives": "Model relational schemas, diagnose slow queries using EXPLAIN ANALYZE, and create composite indexes matching query predicates.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 90,
                        "display_order": 1,
                        "skill_id": skills.get("Query Optimization (SQL)") or skill_domains.get("SQL"),
                        "subtopics": [
                            {"name": "Database Normalization (1NF, 2NF, 3NF)", "description": "Eliminating update anomalies and data redundancy."},
                            {"name": "B-Tree Indexing Mechanics", "description": "Leftmost prefix rule, index scans, bitmap scans, and index-only scans."},
                            {"name": "Query Optimization & EXPLAIN ANALYZE", "description": "Spotting sequential scans on large tables and resolving bottlenecks."}
                        ],
                        "resources": [
                            {
                                "title": "PostgreSQL Indexing and Query Performance Tuning",
                                "description": "How B-Tree indexes work under the hood and how to read execution plans.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# PostgreSQL Indexing and Performance

## 1. B-Tree Index Mechanics
A B-Tree maintains balanced sorted data across disk pages.
When you query `WHERE user_id = ? AND created_at > ?`, a composite index on `(user_id, created_at)` enables a direct index seek.

```sql
CREATE INDEX idx_student_activities ON student_behavior_events(user_id, created_at DESC);
EXPLAIN ANALYZE SELECT * FROM student_behavior_events WHERE user_id = 'bd9cc0b5-8132-49d4-af7f-11dc8fe97d09' ORDER BY created_at DESC LIMIT 20;
```
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-caching-redis",
                        "name": "In-Memory Caching & Redis Architecture",
                        "description": "Cache-aside pattern, TTL invalidation, cache stampede prevention, Redis data structures (Strings, Hashes, Sorted Sets), and pub/sub.",
                        "learning_objectives": "Implement the Cache-Aside pattern with Redis, configure write-through strategies, and prevent cache penetration/stampede.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 75,
                        "display_order": 2,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Cache Patterns: Cache-Aside & Write-Through", "description": "Balancing read latency vs data consistency."},
                            {"name": "Redis Core Data Structures", "description": "Strings, Lists, Sets, Hashes, and Sorted Sets (ZSET) for leaderboards."},
                            {"name": "Cache Invalidation & TTL", "description": "Active vs passive eviction policies (LRU, LFU) and stampede mitigation."}
                        ],
                        "resources": [
                            {
                                "title": "High-Throughput Caching with Redis & Invalidation Strategies",
                                "description": "Architecting resilient caching tiers for high-traffic web applications.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# Redis Caching Architecture

## 1. Cache-Aside Pattern
1. Application receives read request for student profile.
2. Checks Redis: `redis.get(f"student:{id}")`.
3. If Cache Hit: return JSON immediately.
4. If Cache Miss: query PostgreSQL, store result in Redis with a 15-minute TTL, and return.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "FS-SYSTEMS",
                "name": "System Design & Deployment",
                "description": "Full-stack scalable architectures, load balancing, stateless servers, containerization with Docker, and CI/CD pipelines.",
                "icon": "Layers",
                "display_order": 4,
                "topics": [
                    {
                        "slug": "fs-sys-design",
                        "name": "Full-Stack System Design & Scalability",
                        "description": "Vertical vs horizontal scaling, reverse proxies (Nginx), CDN edge caching, database read replicas, and connection pooling.",
                        "learning_objectives": "Architect scalable systems that handle 10,000+ concurrent requests using load balancers, replicas, and stateless application tiers.",
                        "difficulty": "ADVANCED",
                        "estimated_minutes": 110,
                        "display_order": 1,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Horizontal Scaling & Stateless Services", "description": "Offloading session state to Redis so instances can scale dynamically."},
                            {"name": "Database Replication & Read/Write Splits", "description": "Primary-replica topologies and eventual consistency caveats."},
                            {"name": "Rate Limiting & Throttling", "description": "Token bucket and sliding window rate limiting algorithms."}
                        ],
                        "resources": [
                            {
                                "title": "Full-Stack Scalability: From Monolith to Distributed Cloud",
                                "description": "System design trade-offs for modern high-availability applications.",
                                "resource_type": "ARTICLE",
                                "difficulty": "HARD",
                                "estimated_duration_min": 35,
                                "content": """# Scalable Web Architecture & System Design

## 1. Core Principles of Scalability
- **Stateless App Nodes**: Application servers should not hold state in memory; state resides in databases or cache clusters.
- **Connection Pooling**: Reusing TCP database connections using PgBouncer to prevent connection exhaustion.
- **CDN Edge Offloading**: Serving static bundles, media, and cached responses from geographically close edge points.
"""
                            }
                        ]
                    },
                    {
                        "slug": "fs-docker-cicd",
                        "name": "Docker Containerization & CI/CD Pipelines",
                        "description": "Multi-stage Docker builds, container networking, environment variable injection, GitHub Actions workflows, and automated deployment.",
                        "learning_objectives": "Build minimal Docker container images, automate linting and testing in CI/CD, and orchestrate services.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 80,
                        "display_order": 2,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Multi-Stage Dockerfiles", "description": "Separating build tools from runtime footprint for ultra-lean production images."},
                            {"name": "Docker Compose Multi-Container Orchestration", "description": "Configuring frontend, API, database, and Redis networks."},
                            {"name": "Automated CI/CD Pipelines", "description": "Linting, test execution, container registry push, and automated releases."}
                        ],
                        "resources": [
                            {
                                "title": "Modern Containerization and Deployment Workflows",
                                "description": "Practical guide to Dockerizing full-stack web applications and setting up CI pipelines.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# Docker & CI/CD Best Practices

## 1. Multi-Stage Dockerfile Pattern
```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```
"""
                            }
                        ]
                    }
                ]
            }
        ]

        # -------------------------------------------------------------
        # 3. AIML Curriculum
        # -------------------------------------------------------------
        aiml_path = paths_by_code["AIML"]

        aiml_subjects = [
            {
                "code": "AIML-MATH",
                "name": "Mathematical Foundations for AI",
                "description": "Linear algebra, matrix factorizations, multivariate gradient calculus, optimization landscapes, and probability theory.",
                "icon": "Calculator",
                "display_order": 1,
                "topics": [
                    {
                        "slug": "ai-linear-algebra",
                        "name": "Linear Algebra: Vectors, Matrices & Eigenvalues",
                        "description": "Vector spaces, dot products, matrix multiplication invariants, determinants, eigenvalues, eigenvectors, and Singular Value Decomposition (SVD).",
                        "learning_objectives": "Compute projections, understand orthogonal transformations, and intuitively apply SVD/PCA for dimensionality reduction.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 80,
                        "display_order": 1,
                        "skill_id": skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Vectors & Matrix Transformations", "description": "Linear combinations, span, basis, and coordinate transformations."},
                            {"name": "Eigenvalues & Eigenvectors", "description": "Characteristic equation, diagonalizability, and principal directions."},
                            {"name": "Singular Value Decomposition (SVD)", "description": "U Sigma V^T decomposition and low-rank matrix approximations."}
                        ],
                        "resources": [
                            {
                                "title": "Intuitive Linear Algebra for Machine Learning Engineers",
                                "description": "Visualizing high-dimensional vector spaces and matrix decompositions.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# Linear Algebra Foundations for Machine Learning

## 1. Matrices as Geometric Transformations
A matrix transformation $T(x) = Ax$ stretches, rotates, and shears space.
The **eigenvectors** are directions where the transformation only stretches (scales) without changing orientation:
$$Av = \\lambda v$$
where $\\lambda$ is the eigenvalue. In PCA, principal components are eigenvectors of the feature covariance matrix!
"""
                            }
                        ]
                    },
                    {
                        "slug": "ai-calculus-opt",
                        "name": "Multivariate Calculus & Gradient Optimization",
                        "description": "Partial derivatives, gradient vectors, Hessian matrices, chain rule in vector form, and stochastic gradient descent dynamics.",
                        "learning_objectives": "Derive backpropagation gradient updates and analyze convergence of Momentum, RMSProp, and Adam optimizers.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 90,
                        "display_order": 2,
                        "skill_id": skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Gradients & The Jacobian Matrix", "description": "Direction of steepest ascent and multivariate chain rule."},
                            {"name": "Hessian Matrix & Curvature", "description": "Second derivatives, convexity, saddle points, and condition numbers."},
                            {"name": "First-Order Optimization Algorithms", "description": "SGD with momentum, Adam adaptive learning rates, and gradient clipping."}
                        ],
                        "resources": [
                            {
                                "title": "Calculus for Deep Learning: From Gradients to Adam Optimizer",
                                "description": "Mathematical mechanics of optimization surfaces and adaptive learning rates.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# Optimization in Machine Learning

## 1. Gradient Descent Invariant
Parameters $\\theta$ are iteratively updated opposite to the gradient of the loss function $\\nabla L(\\theta)$:
$$\\theta_{t+1} = \\theta_t - \\eta \\nabla L(\\theta_t)$$
Adam combines momentum (first moment of gradients) with RMSProp (second moment of gradients) to adapt per-parameter learning rates.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "AIML-CORE",
                "name": "Core Machine Learning & Algorithms",
                "description": "Supervised algorithms, regression, decision trees, ensemble bagging/boosting, clustering, and cross-validation methodology.",
                "icon": "Brain",
                "display_order": 2,
                "topics": [
                    {
                        "slug": "ai-feature-engineering",
                        "name": "Feature Engineering, Scaling & EDA",
                        "description": "Handling missing values, one-hot vs target encoding, standard vs min-max scaling, outlier detection, and correlation analysis.",
                        "learning_objectives": "Prepare clean tabular pipelines without data leakage and engineer predictive interaction features.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 70,
                        "display_order": 1,
                        "skill_id": skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Preventing Data Leakage", "description": "Fitting scalers and imputers solely on training folds."},
                            {"name": "Categorical Encodings", "description": "Cardinality management, frequency encoding, and target encoding with regularization."},
                            {"name": "Outlier Detection & Imputation", "description": "IQR boundaries, Z-scores, and KNN-based imputation."}
                        ],
                        "resources": [
                            {
                                "title": "The Art of Feature Engineering & Leakage Prevention",
                                "description": "Industry practices for building bulletproof tabular preprocessing pipelines.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": """# Feature Engineering & Preprocessing

## 1. The Golden Rule of Data Leakage
Never fit any scaler, normalizer, or encoder on the entire dataset. Always split into Train/Validation/Test FIRST, fit transformers solely on Train, and use `.transform()` on Validation/Test.
"""
                            }
                        ]
                    },
                    {
                        "slug": "ai-supervised-models",
                        "name": "Supervised Learning: Trees, Ensembles & SVMs",
                        "description": "Linear/Logistic Regression, Decision Trees (entropy/Gini impurity), Random Forests, Gradient Boosted Trees (XGBoost/LightGBM), and SVMs.",
                        "learning_objectives": "Compare inductive biases, tune hyperparameters to resolve bias-variance tradeoff, and interpret tree feature importances.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 95,
                        "display_order": 2,
                        "skill_id": skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Bias-Variance Tradeoff", "description": "Overfitting vs underfitting, regularization penalties (L1/L2 Lasso/Ridge)."},
                            {"name": "Decision Trees & Splitting Criteria", "description": "Information gain, Shannon entropy, and Gini impurity."},
                            {"name": "Ensemble Methods: Bagging vs Boosting", "description": "Random Forests vs Gradient Boosting (XGBoost, CatBoost)."}
                        ],
                        "resources": [
                            {
                                "title": "Tree-Based Models: From Decision Stumps to XGBoost",
                                "description": "Mathematical comparison of gradient boosting vs random forest variance reduction.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# Supervised Learning & Ensemble Methods

## 1. Bagging vs Boosting
- **Bagging (Random Forest)**: Trains independent trees on bootstrap samples with random feature subsets. Primarily reduces **variance** (prevents overfitting).
- **Boosting (XGBoost)**: Trains sequential trees where each tree fits the negative gradient (residuals) of previous predictions. Primarily reduces **bias**.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "AIML-DEEP",
                "name": "Deep Learning & Neural Architectures",
                "description": "Multilayer perceptrons, convolutional networks for computer vision, sequence models, and self-attention transformer mechanisms.",
                "icon": "Cpu",
                "display_order": 3,
                "topics": [
                    {
                        "slug": "ai-neural-foundations",
                        "name": "Perceptrons, Activations & Backpropagation",
                        "description": "Feedforward neural networks, activation functions (ReLU, GELU, Sigmoid), vanishing/exploding gradients, and Batch Normalization.",
                        "learning_objectives": "Implement a forward-backward pass from scratch and select proper activation and weight initialization schemes (He/Xavier).",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 90,
                        "display_order": 1,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Activation Functions & Gradient Dynamics", "description": "Vanishing gradient problem in Sigmoid/Tanh and the dominance of ReLU/GELU."},
                            {"name": "Batch Normalization & LayerNorm", "description": "Internal covariate shift mitigation and gradient smoothing."},
                            {"name": "Backpropagation Algorithm", "description": "Computational graphs and reverse-mode automatic differentiation."}
                        ],
                        "resources": [
                            {
                                "title": "Neural Network Foundations & Backpropagation Calculus",
                                "description": "Step-by-step mathematical derivation of reverse-mode automatic differentiation.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# Neural Networks & Computational Graphs

## 1. Backpropagation Invariant
By applying the multivariate chain rule across nodes in a directed acyclic computation graph:
$$\\frac{\\partial L}{\\partial W^{[l]}} = \\delta^{[l]} (a^{[l-1]})^T$$
Batch Normalization normalizes activations across the mini-batch dimension, enabling significantly higher learning rates and stabilizing deep convergence.
"""
                            }
                        ]
                    },
                    {
                        "slug": "ai-transformers",
                        "name": "Attention Mechanisms & Transformer Architecture",
                        "description": "Scaled dot-product attention, multi-head self-attention, positional embeddings, encoder-decoder architectures, and BERT/GPT paradigms.",
                        "learning_objectives": "Derive Q, K, V attention matrices, compute quadratic sequence complexity, and understand causal masking.",
                        "difficulty": "ADVANCED",
                        "estimated_minutes": 110,
                        "display_order": 2,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Query, Key, Value Formulation", "description": "Softmax((QK^T) / sqrt(d_k)) * V attention equation breakdown."},
                            {"name": "Multi-Head Attention", "description": "Jointly attending to information from different representation subspaces."},
                            {"name": "Causal Masking & Autoregressive Decoding", "description": "Preventing token leakage during training in decoder-only models (GPT)."}
                        ],
                        "resources": [
                            {
                                "title": "The Illustrated Transformer: Attention Is All You Need",
                                "description": "In-depth guide to modern Transformer architectures driving contemporary LLMs.",
                                "resource_type": "ARTICLE",
                                "difficulty": "HARD",
                                "estimated_duration_min": 35,
                                "content": """# The Transformer Architecture

## 1. Scaled Dot-Product Attention
$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$
Dividing by $\\sqrt{d_k}$ prevents dot products from growing excessively large in high dimensions, which would otherwise push the softmax into regions with vanishing gradients.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "AIML-PRODUCTION",
                "name": "MLOps, LLMs & Production AI",
                "description": "Large language model integrations, Retrieval-Augmented Generation (RAG), vector embeddings, model deployment, and drift monitoring.",
                "icon": "Terminal",
                "display_order": 4,
                "topics": [
                    {
                        "slug": "ai-llm-rag",
                        "name": "LLM Integration, Vector Databases & RAG",
                        "description": "Prompt engineering patterns, tokenization, dense embeddings, vector indexing (HNSW), chunking strategies, and grounded retrieval.",
                        "learning_objectives": "Design production RAG pipelines with semantic vector search, reranking, and hallucination guardrails.",
                        "difficulty": "ADVANCED",
                        "estimated_minutes": 100,
                        "display_order": 1,
                        "skill_id": skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Text Chunking & Embedding Generation", "description": "Recursive character splitters, token boundaries, and embedding model selection."},
                            {"name": "Vector Search & Indexing (HNSW)", "description": "Approximate nearest neighbors (ANN), cosine similarity vs dot product."},
                            {"name": "Retrieval Augmentation & Reranking", "description": "Cross-encoders, reciprocal rank fusion (RRF), and context window packing."}
                        ],
                        "resources": [
                            {
                                "title": "Architecting Enterprise Retrieval-Augmented Generation (RAG)",
                                "description": "Complete architectural blueprint for low-latency, accurate LLM search systems.",
                                "resource_type": "ARTICLE",
                                "difficulty": "HARD",
                                "estimated_duration_min": 30,
                                "content": """# Production RAG Architecture

## 1. Core RAG Workflow
1. **Ingestion**: Documents are split into semantic chunks (e.g. 500 tokens with 50-token overlap).
2. **Embedding**: Embedded into a dense vector space using an embedding model.
3. **Indexing**: Stored in a vector database utilizing Hierarchical Navigable Small World (HNSW) indexes.
4. **Retrieval**: User query is embedded, top-$k$ nearest chunks are retrieved, reranked by a cross-encoder, and injected into the LLM system prompt.
"""
                            }
                        ]
                    }
                ]
            }
        ]

        # -------------------------------------------------------------
        # 4. DATA_ANALYST Curriculum
        # -------------------------------------------------------------
        da_path = paths_by_code["DATA_ANALYST"]

        da_subjects = [
            {
                "code": "DA-SQL",
                "name": "Advanced SQL & Data Warehousing",
                "description": "Complex joins, analytical window functions, common table expressions (CTEs), star schemas, and ETL data pipeline modeling.",
                "icon": "Database",
                "display_order": 1,
                "topics": [
                    {
                        "slug": "da-sql-joins",
                        "name": "Complex Joins, Subqueries & Aggregations",
                        "description": "INNER, LEFT, RIGHT, FULL OUTER joins, self-joins, correlated subqueries, GROUP BY with HAVING, and NULL handling.",
                        "learning_objectives": "Write production analytical SQL queries joining disparate enterprise tables with zero accidental cartesian duplicates.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 70,
                        "display_order": 1,
                        "skill_id": skills.get("Joins & Subqueries (SQL)") or skill_domains.get("SQL"),
                        "subtopics": [
                            {"name": "Join Types & Cartesian Prevention", "description": "Understanding matching criteria and avoiding many-to-many multiplication."},
                            {"name": "Grouping & Multi-Level Aggregations", "description": "GROUP BY, HAVING vs WHERE clauses, and counting distinct keys."},
                            {"name": "Common Table Expressions (CTEs)", "description": "Structuring readable multi-step queries using WITH clauses."}
                        ],
                        "resources": [
                            {
                                "title": "Advanced SQL Querying: Mastering Joins, Aggregations & CTEs",
                                "description": "Practical guide to writing performant analytical queries for placement interviews.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 25,
                                "content": """# Advanced Analytical SQL: Joins & Aggregations

## 1. JOIN Types and Cartesian Guardrails
When joining tables on non-unique foreign keys, duplicate rows multiply unexpectedly.
Always verify row counts before and after joining:

```sql
WITH MonthlyPlacements AS (
  SELECT 
    d.department_name,
    DATE_TRUNC('month', p.offer_date) AS placement_month,
    COUNT(p.id) AS total_placed,
    AVG(p.ctc_lpa) AS avg_package
  FROM placements p
  JOIN students s ON p.student_id = s.id
  JOIN departments d ON s.department_id = d.id
  WHERE p.status = 'ACCEPTED'
  GROUP BY d.department_name, DATE_TRUNC('month', p.offer_date)
)
SELECT * FROM MonthlyPlacements ORDER BY total_placed DESC;
```
"""
                            }
                        ]
                    },
                    {
                        "slug": "da-window-functions",
                        "name": "SQL Analytical Window Functions",
                        "description": "ROW_NUMBER, RANK, DENSE_RANK, NTILE, LAG, LEAD, and cumulative rolling sums using PARTITION BY and ORDER BY clauses.",
                        "learning_objectives": "Calculate running totals, month-over-month growth metrics, and top-$N$ performers per category using window partitions.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 85,
                        "display_order": 2,
                        "skill_id": skills.get("Window Functions (SQL)") or skill_domains.get("SQL"),
                        "subtopics": [
                            {"name": "Ranking Functions", "description": "Comparing ROW_NUMBER(), RANK(), and DENSE_RANK() tie-breaker behaviors."},
                            {"name": "Value Offsets: LAG & LEAD", "description": "Calculating prior-period comparisons and delta changes."},
                            {"name": "Rolling Aggregations & Frame Clauses", "description": "ROWS BETWEEN 6 PRECEDING AND CURRENT ROW moving averages."}
                        ],
                        "resources": [
                            {
                                "title": "SQL Window Functions in Production Business Analytics",
                                "description": "Comprehensive tutorial on partitioning, ranking, running aggregates, and frame specifications.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 30,
                                "content": """# SQL Window Functions

## 1. Syntax & Mechanics
Window functions perform calculations across a set of table rows that are related to the current row, without collapsing rows like `GROUP BY`:
```sql
SELECT 
  student_name,
  department,
  cgpa,
  RANK() OVER(PARTITION BY department ORDER BY cgpa DESC) AS dept_rank,
  DENSE_RANK() OVER(PARTITION BY department ORDER BY cgpa DESC) AS dept_dense_rank
FROM student_records;
```
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "DA-STATS",
                "name": "Business Statistics & Hypothesis Testing",
                "description": "Descriptive measures, probability distributions, Central Limit Theorem, hypothesis testing, p-values, and A/B test analysis.",
                "icon": "PieChart",
                "display_order": 2,
                "topics": [
                    {
                        "slug": "da-descriptive-stats",
                        "name": "Descriptive Statistics & Data Distributions",
                        "description": "Mean, median, mode, variance, standard deviation, interquartile range (IQR), skewness, kurtosis, and the Normal distribution.",
                        "learning_objectives": "Summarize continuous distributions, recognize skewed data where median outperforms mean, and calculate percentiles.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 65,
                        "display_order": 1,
                        "skill_id": skills.get("Data Interpretation (QUANT)") or skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Measures of Central Tendency & Spread", "description": "Robustness of median/IQR vs sensitivity of mean/standard deviation to outliers."},
                            {"name": "Normal Distribution & Empirical 68-95-99.7 Rule", "description": "Z-score normalization and probability density curves."},
                            {"name": "Data Skewness & Transformations", "description": "Right vs left skew and log transformations for power-law distributions."}
                        ],
                        "resources": [
                            {
                                "title": "Essential Business Statistics for Placement Interviews",
                                "description": "Core descriptive measures, outlier identification, and real-world distribution interpretations.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": """# Business Statistics Foundations

## 1. Mean vs Median in Placement CTC Distributions
Compensation distributions are typically right-skewed with a few very high packages.
In right-skewed data:
$$\\text{Mean} > \\text{Median} > \\text{Mode}$$
Reporting the median package provides a much more honest and accurate metric of typical student outcomes than an outlier-inflated mean.
"""
                            }
                        ]
                    },
                    {
                        "slug": "da-hypothesis-testing",
                        "name": "Hypothesis Testing, P-Values & A/B Experiments",
                        "description": "Null vs alternative hypotheses, Type I vs Type II errors, statistical significance (alpha), Z-tests, two-sample t-tests, and chi-square tests.",
                        "learning_objectives": "Formulate testable business hypotheses, interpret p-values correctly, and compute required sample sizes for A/B testing.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 85,
                        "display_order": 2,
                        "skill_id": skills.get("Permutations & Probability (QUANT)") or skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Formulating Hypotheses & Significance Level", "description": "Null hypothesis (H0), alternative (H1), and setting alpha = 0.05."},
                            {"name": "Type I vs Type II Errors & Power", "description": "False positive risk (alpha) vs false negative risk (beta), and statistical power (1 - beta)."},
                            {"name": "T-Tests & P-Value Interpretation", "description": "Independent two-sample t-tests and interpreting probabilities of observing extreme effects."}
                        ],
                        "resources": [
                            {
                                "title": "A/B Testing and Hypothesis Evaluation in Modern Business",
                                "description": "Statistical decision-making frameworks for product and business analysts.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# Hypothesis Testing & A/B Experimentation

## 1. The P-Value Invariant
The **p-value** is the probability of observing test results at least as extreme as the actual observed results, assuming the null hypothesis ($H_0$) is strictly true.
A p-value < 0.05 means that if there were truly no difference, such a result would occur by random chance less than 5% of the time.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "DA-VIZ",
                "name": "Data Visualization & Dashboards",
                "description": "Visual encoding principles, chart selection matrix, Power BI/Tableau design, KPI summaries, and stakeholder communication.",
                "icon": "BarChart",
                "display_order": 3,
                "topics": [
                    {
                        "slug": "da-viz-principles",
                        "name": "Visual Perception & Dashboard Design UX",
                        "description": "Preattentive visual attributes (color, size, position), Gestalt grouping principles, chart selection heuristics, and minimizing cognitive load.",
                        "learning_objectives": "Choose optimal chart types for comparisons, distributions, and trends, while avoiding chart junk and deceptive axes.",
                        "difficulty": "BEGINNER",
                        "estimated_minutes": 60,
                        "display_order": 1,
                        "skill_id": skills.get("Data Interpretation (QUANT)") or skill_domains.get("QUANT"),
                        "subtopics": [
                            {"name": "Chart Selection Matrix", "description": "When to use bar charts, line graphs, scatter plots, and heatmaps vs pie charts."},
                            {"name": "Cognitive Load & Preattentive Attributes", "description": "Using color intentionally as an alert rather than visual noise."},
                            {"name": "Accessible & Honest Visualizations", "description": "Zero baseline on bar charts, dual-axis cautions, and color-blind safety."}
                        ],
                        "resources": [
                            {
                                "title": "Dashboard UX & Strategic Data Visualization",
                                "description": "Frameworks for designing clear, actionable business dashboards.",
                                "resource_type": "ARTICLE",
                                "difficulty": "EASY",
                                "estimated_duration_min": 20,
                                "content": """# Principles of Strategic Data Visualization

## 1. Chart Selection Guide
- **Bar Chart**: Discrete category comparisons (always start y-axis at 0!).
- **Line Chart**: Continuous trends over time.
- **Scatter Plot**: Relationship and correlation between two continuous numerical variables.
- **Heatmap**: 2D density matrices or cross-tabulated category intensities.
"""
                            }
                        ]
                    }
                ]
            },
            {
                "code": "DA-PYTHON",
                "name": "Python for Data Analytics",
                "description": "NumPy vectorized operations, Pandas DataFrames, data cleaning, groupby operations, and statistical visualization with Seaborn.",
                "icon": "Code",
                "display_order": 4,
                "topics": [
                    {
                        "slug": "da-pandas-numpy",
                        "name": "Pandas Data Wrangling & Cleaning Workflows",
                        "description": "DataFrame indexing (`.loc`, `.iloc`), handling missing data (`fillna`, `dropna`), merging/joining DataFrames, and `.apply()` vs vectorized operations.",
                        "learning_objectives": "Manipulate tabular datasets with vectorized Pandas methods, reshape data using pivot tables, and compute grouped statistics.",
                        "difficulty": "INTERMEDIATE",
                        "estimated_minutes": 85,
                        "display_order": 1,
                        "skill_id": skills.get("Arrays & Strings (PROGRAMMING)") or skill_domains.get("PROGRAMMING"),
                        "subtopics": [
                            {"name": "Vectorized Operations vs Slow Python Loops", "description": "NumPy broadcasting and speedups over iterrows()."},
                            {"name": "Filtering, Grouping & Aggregating", "description": "groupby().agg() with multiple named output columns."},
                            {"name": "Reshaping: Melt & Pivot Tables", "description": "Converting between wide and long format datasets."}
                        ],
                        "resources": [
                            {
                                "title": "High-Performance Data Wrangling with Pandas & NumPy",
                                "description": "Best practices for analytical pipelines, memory reduction, and clean data transformations.",
                                "resource_type": "ARTICLE",
                                "difficulty": "MEDIUM",
                                "estimated_duration_min": 25,
                                "content": """# Production Pandas Data Wrangling

## 1. Vectorization vs Loops
Never loop through DataFrame rows with `for index, row in df.iterrows()`! It incurs massive overhead.
Instead, use vectorized series expressions:

```python
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('placement_records.csv')

# Efficient grouped aggregation
summary = (
    df.groupby(['department', 'tier'])
    .agg(
        total_students=('id', 'count'),
        avg_package=('ctc_lpa', 'mean'),
        max_package=('ctc_lpa', 'max'),
        median_cgpa=('cgpa', 'median')
    )
    .reset_index()
)
```
"""
                            }
                        ]
                    }
                ]
            }
        ]

        # -------------------------------------------------------------
        # 5. Seed subjects & topics helper
        # -------------------------------------------------------------
        all_career_specs = [
            (fullstack_path, fullstack_subjects),
            (aiml_path, aiml_subjects),
            (da_path, da_subjects),
        ]

        for path_obj, subjects_data in all_career_specs:
            print(f"\nProcessing Curriculum for Career Path: {path_obj.title} ({path_obj.code})...")
            for s_spec in subjects_data:
                subject = (
                    db.query(RoadmapSubject)
                    .filter(
                        RoadmapSubject.career_path_id == path_obj.id,
                        RoadmapSubject.code == s_spec["code"],
                    )
                    .first()
                )
                if not subject:
                    subject = RoadmapSubject(
                        career_path_id=path_obj.id,
                        code=s_spec["code"],
                        name=s_spec["name"],
                        description=s_spec["description"],
                        icon=s_spec["icon"],
                        display_order=s_spec["display_order"],
                    )
                    db.add(subject)
                    db.flush()
                    print(f"  Created Subject: {subject.name}")
                else:
                    subject.name = s_spec["name"]
                    subject.description = s_spec["description"]
                    subject.icon = s_spec["icon"]
                    subject.display_order = s_spec["display_order"]
                    db.flush()

                for t_spec in s_spec.get("topics", []):
                    topic = (
                        db.query(RoadmapTopic)
                        .filter(
                            RoadmapTopic.subject_id == subject.id,
                            RoadmapTopic.slug == t_spec["slug"],
                        )
                        .first()
                    )
                    if not topic:
                        topic = RoadmapTopic(
                            subject_id=subject.id,
                            slug=t_spec["slug"],
                            name=t_spec["name"],
                            description=t_spec["description"],
                            learning_objectives=t_spec["learning_objectives"],
                            difficulty=t_spec["difficulty"],
                            estimated_minutes=t_spec["estimated_minutes"],
                            display_order=t_spec["display_order"],
                            skill_id=t_spec.get("skill_id"),
                            dsa_topic_id=t_spec.get("dsa_topic_id"),
                        )
                        db.add(topic)
                        db.flush()
                        print(f"    Created Topic: {topic.name} (Slug: {topic.slug})")
                    else:
                        topic.name = t_spec["name"]
                        topic.description = t_spec["description"]
                        topic.learning_objectives = t_spec["learning_objectives"]
                        topic.difficulty = t_spec["difficulty"]
                        topic.estimated_minutes = t_spec["estimated_minutes"]
                        topic.display_order = t_spec["display_order"]
                        if t_spec.get("skill_id"):
                            topic.skill_id = t_spec["skill_id"]
                        if t_spec.get("dsa_topic_id"):
                            topic.dsa_topic_id = t_spec["dsa_topic_id"]
                        db.flush()

                    # Seed subtopics
                    for st_idx, st_spec in enumerate(t_spec.get("subtopics", [])):
                        existing_st = (
                            db.query(RoadmapSubtopic)
                            .filter(
                                RoadmapSubtopic.topic_id == topic.id,
                                RoadmapSubtopic.name == st_spec["name"],
                            )
                            .first()
                        )
                        if not existing_st:
                            subtopic = RoadmapSubtopic(
                                topic_id=topic.id,
                                name=st_spec["name"],
                                description=st_spec["description"],
                                display_order=st_idx + 1,
                            )
                            db.add(subtopic)

                    # Seed learning resources
                    for r_spec in t_spec.get("resources", []):
                        existing_r = (
                            db.query(LearningResource)
                            .filter(
                                LearningResource.topic_id == topic.id,
                                LearningResource.title == r_spec["title"],
                            )
                            .first()
                        )
                        if not existing_r:
                            resource = LearningResource(
                                topic_id=topic.id,
                                title=r_spec["title"],
                                description=r_spec["description"],
                                resource_type=r_spec["resource_type"],
                                content=r_spec["content"],
                                difficulty=r_spec["difficulty"],
                                estimated_duration_min=r_spec["estimated_duration_min"],
                                status="PUBLISHED",
                            )
                            db.add(resource)

        db.commit()
        print("\nAll Career Paths successfully populated with complete curriculum!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding curriculum: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_curricula()
