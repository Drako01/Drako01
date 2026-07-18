# GitHub profile audit

Audit date: 2026-07-18.

## Executive assessment

The profile has substantial professional experience behind it, but the public signal does not yet match
that experience. The previous README mixed strong production claims with a very broad technology matrix,
generic project rows, seven external metric widgets, and a visual journey that made the page longer without
making the strongest work easier to evaluate.

The main profile-level issue is the pinned repository set. It currently prioritizes reference material and
early experiments over current backend, product, and architecture work.

## Public profile findings

| Surface | Current state | Recommendation |
| --- | --- | --- |
| Name | Alejandro Daniel Di Stefano | Keep. It is complete and searchable. |
| Username | Drako01 | Keep. It is established across the account. |
| Bio | `<Full Stack Developer />` | Replace with a specific senior positioning statement. |
| Company | armotusitio.com.ar | Keep, but display it consistently as ArmotuSitio. |
| Website | armotusitio.com.ar | Keep or use the personal portfolio as the primary link. |
| Location | Quilmes | Expand to `Buenos Aires, Argentina` for international context. |
| Avatar | Characterized Joker image | Replace with a current professional headshot using a neutral crop and background. |
| Status | `A veces tardo en Responder...` | Remove; it creates friction before a recruiter or client starts a conversation. |
| Social link | Photography-focused Instagram | Replace with LinkedIn if only one professional social link is shown. |
| README | Strong content, excessive breadth | Replaced with a shorter product- and architecture-led narrative. |
| Metrics | Seven external widgets | Reduced to activity, summary statistics, and repository languages. |

Recommended bio, within GitHub's short profile format:

> Full Stack Software Engineer · PHP, Go, React & Next.js · APIs, SaaS, e-commerce and business platforms.

## Repository portfolio classification

The account contains 140 public repositories. The classification below is brand-oriented: it determines
what a recruiter should see first, not whether a repository has personal or educational value.

The current pins are `commands-github`, `portfolio`, `MongoDB--Commands`, `api-rest-pagos`, `Pybot`, and
`jugando_con_typescript`. Only `api-rest-pagos` should remain in the primary set. The others communicate
reference notes, early portfolio work, or focused practice more strongly than senior product ownership.

### Featured now

These repositories provide the clearest public evidence of current engineering ability:

- `Drako01` — professional profile and portfolio entry point.
- `backend_lrdu` — PHP 8 REST API, MySQL, JWT, RBAC, filters, pagination, and layered architecture.
- `react-chatflow` — reusable React conversation-flow component with modular state-based design.
- `api-rest-pagos` — end-to-end payments management application with Node.js, React, and PostgreSQL.
- `e-commerce-market` — full stack commerce application with React and Node.js.
- `websocket-java` — focused real-time server implementation; useful as secondary backend evidence.

### Production work represented as case studies

These are the strongest current products, but their source repositories are private. They should be shown
through live products or sanitized case studies, not presented as public code:

- `armotusitio2.0` — Next.js, PHP, MySQL, CRM, client portal, analytics, RBAC, 2FA, queues, and automation.
- `solution_bellagema4.0` — production e-commerce, backoffice, payments, shipping, loyalty, and email center.
- `velisa` — multi-application commerce platform with frontend, admin, backend, and shared design system.
- `auth_server_go` — Go authentication, mitigation, multi-database persistence, metrics, and cloud delivery.
- `ticket-service` — Go traffic analysis, mitigation, Redis, Prometheus, Grafana, and load-oriented design.
- `estudiochb` — production client landing with responsive, accessible static delivery.

### Formation and teaching

Keep these repositories public when they support students or demonstrate teaching history, but do not pin
them. Their names and descriptions should explicitly say `teaching`, `course material`, or `student work`.

- Repositories matching `javascript-*`, `java-*`, `SQL_Flex-*`, `BE_*`, `be_*`, `dw_*`, and `clase-*`.
- `55290---JavaScript`, `angular__59435`, `java-coderhouse--53330`, and `coder-backend-32160`.
- `programacion_web_santino`, `javascript__santino`, `programacion_matias`, and `santino_ts`.
- `bootcamp_java_educacionit`, `bootcamp-java-educacionit`, and `java-udemy`.
- `Trabajo-Practico---Python`, `Diplomatura_Python_UTN.BA`, and other course deliverables.

### Experiments and focused demos

Keep as a lab archive. Add concise descriptions where missing, and do not pin unless a project is expanded
with tests, documentation, a demo, and a clear maintenance status.

- `sf_new_server`, `ProductApi`, `Pybot`, `qr-python`, `websocket_php`, and `json-server-api-main`.
- `jugando_con_typescript`, `MongoDB--Commands`, `commands-github`, and `carrousel-js`.
- `google-sheets-test`, `formulario-whatsapp`, `encriptar_pass_crypt`, and `exportar_excel`.
- `app-music`, `kotlin_new`, `python_web`, `react-star-wars`, and `react-firebase-auth`.
- `coderhouse-rockola`, `app-spring-boot`, `desafio-integrador-01`, and `ProductApi`.

### Historical and obsolete portfolio material

Preserve for history, but archive where practical and remove from the professional narrative:

- `portfolio`, `cv`, `Maquetado_Avanzado`, and earlier personal site repositories.
- `BellaGema-V2.0`, `BellaGema-V3.0`, `BellaGema_v_4.0`, `bellagema_october`, and related superseded versions.
- `Lonne-Open`, `lonne-open-ReactApp`, and `lonne-open-proshop2.0` after confirming no active dependency.
- Generic or ambiguous repositories such as `Proyecto`, `Trabajo-Practico`, `master`, `oldest`, and `back`.
- Early delivery repositories matching `Entrega-*`, `Desafio-*`, `Modulo-*`, and `M5`.
- Small visual exercises such as `Menu-3D-con-Perspectiva`, `css-cards`, and `homer-page`.

### Forks and reference repositories

These can remain starred or forked, but they should not be confused with authored portfolio work:

- `agones`, `n8n`, `spec-kit`, `skill-icons`, `markdownlint`, and `ecommerce-react`.
- `precourse-materials`, `badwords`, `List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words`, and `css-cards`.
- Profile or reference forks such as `eAntillon`, `raviprakash11`, `daweedkob`, and `readme.md`.

## Recommended pinned repositories

Use this order after the public repositories have accurate descriptions, topics, and README files:

1. `Drako01` — the profile itself and the entry point to private production case studies.
1. `backend_lrdu` — strongest public PHP/backend architecture evidence.
1. `react-chatflow` — reusable React and frontend architecture evidence.
1. `api-rest-pagos` — public end-to-end JavaScript product evidence.
1. `e-commerce-market` — additional full stack commerce evidence.
1. `websocket-java` — real-time backend breadth until a stronger public Go case study is available.

The next high-impact repository investment is a sanitized public Go case study. `sf_new_server` is not ready
to fill that role because it has no README and minimal public evidence.

## Image and link audit

The previous README referenced one local PNG, multiple remote badge providers, a technology icon aggregator,
five statistics providers, and a Mermaid diagram. The local image existed, but its white distressed wordmark
had low contrast in GitHub light mode. Remote statistics increased the risk of intermittent empty sections.

The redesign uses:

- Local SVG assets for the hero and every featured project.
- Lowercase, descriptive filenames without spaces.
- Explicit alternative text for every image.
- A single external badge provider and a single external metrics provider.
- HTTPS links to live products, GitHub, LinkedIn, and the personal portfolio.

## Follow-up actions outside this repository

- Update the GitHub bio and location using the copy above.
- Replace the photography Instagram profile link with LinkedIn.
- Apply the recommended pinned repository order.
- Add descriptions and topics to public repositories that are selected for pinning.
- Archive superseded BellaGema, portfolio, and course-delivery repositories after dependency review.
- Publish a sanitized Go architecture repository with tests, benchmarks, diagrams, and no client secrets.
