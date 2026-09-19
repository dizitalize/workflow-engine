# AGENTS.md

# Custom Workflow Automation Engine

## 1. PROJECT MISSION

Build a production-ready, extensible workflow automation engine similar in concept to n8n.

The system must allow users to visually define and execute workflows consisting of connected nodes.

Examples:

```text
Schedule
   ↓
AI Generate Text
   ↓
AI Generate Image
   ↓
Instagram Publish
   ↓
WhatsApp Send
   ↓
Email Send
```

The system must eventually support an unlimited number of workflow types and integrations.

The architecture must prioritize:

* loose coupling
* modularity
* extensibility
* maintainability
* testability
* reliability
* security
* developer experience

The workflow engine is the core product.

Instagram, WhatsApp, Email, Slack, Telegram, AI providers, databases, etc. are integrations/plugins and must NOT become part of the core engine.

---

# 2. CURRENT SCOPE

This repository currently focuses on the BACKEND.

Do NOT build frontend code unless explicitly requested.

Do NOT introduce:

* React
* Next.js
* React Flow
* Tailwind
* Storybook
* frontend-specific abstractions

The future frontend will consume the backend APIs and node metadata.

---

# 3. TECHNOLOGY STACK

Primary stack:

* Python 3.12+
* FastAPI
* Pydantic v2
* PostgreSQL
* SQLAlchemy 2.x
* Alembic
* Redis
* Background workers / queue
* pytest
* httpx
* Docker Compose

Use async Python where it provides a real benefit.

Use type hints throughout the project.

Avoid adding technologies unless there is a clear architectural reason.

---

# 4. ARCHITECTURAL PRINCIPLE

The most important rule:

> THE CORE WORKFLOW ENGINE MUST NEVER DEPEND ON A SPECIFIC INTEGRATION.

The core engine must not contain logic such as:

```python
if node.type == "instagram":
    ...
```

or:

```python
if node.type == "whatsapp":
    ...
```

or:

```python
if node.type == "email":
    ...
```

This is forbidden.

Instead:

```text
Workflow Definition
        ↓
Graph Executor
        ↓
Node Registry
        ↓
Node Implementation
        ↓
Integration Adapter
        ↓
External API
```

Adding a new integration should normally require adding a new node/plugin without modifying the core execution engine.

---

# 5. ARCHITECTURE STYLE

Use a modular monolith initially.

Do NOT create microservices prematurely.

The system should be internally modular enough that individual components can later be extracted into services if scale requires it.

Preferred conceptual architecture:

```text
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      REST API       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Application       │
                    │     Services        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Workflow Engine    Credentials      Scheduler
              │
              ▼
        Graph Executor
              │
              ▼
         Node Registry
              │
       ┌──────┼────────┐
       ▼      ▼        ▼
     AI     Social   Communication
    Nodes    Nodes       Nodes
```

Infrastructure:

```text
PostgreSQL
Redis
Worker
Scheduler
```

---

# 6. DIRECTORY STRUCTURE

Use a structure similar to:

```text
/
├── AGENTS.md
├── README.md
├── ARCHITECTURE.md
├── API.md
├── DATABASE.md
├── SECURITY.md
├── TESTING.md
├── NODE_DEVELOPMENT.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── v1/
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   │
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   │
│   │   ├── models/
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── repositories/
│   │   │
│   │   ├── services/
│   │   │
│   │   ├── workflow/
│   │   │   ├── engine/
│   │   │   ├── graph/
│   │   │   ├── execution/
│   │   │   ├── context/
│   │   │   ├── expressions/
│   │   │   ├── validation/
│   │   │   └── registry/
│   │   │
│   │   ├── nodes/
│   │   │   ├── base/
│   │   │   ├── triggers/
│   │   │   ├── logic/
│   │   │   ├── transform/
│   │   │   ├── utility/
│   │   │   └── ai/
│   │   │
│   │   ├── integrations/
│   │   │   ├── instagram/
│   │   │   ├── whatsapp/
│   │   │   └── email/
│   │   │
│   │   ├── credentials/
│   │   │
│   │   ├── scheduler/
│   │   │
│   │   ├── queue/
│   │   │
│   │   └── workers/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   └── alembic/
│
├── docker-compose.yml
├── .env.example
└── pyproject.toml
```

Adapt the structure when necessary, but preserve the architectural separation.

---

# 7. CORE DOMAIN

The primary domain concepts are:

```text
Workflow
WorkflowVersion
WorkflowNode
WorkflowEdge
WorkflowExecution
NodeExecution
Credential
Schedule
Webhook
```

The core engine must operate on these concepts.

---

# 8. WORKFLOW

A workflow contains:

* id
* workspace/tenant id
* name
* description
* status
* active version
* created_by
* created_at
* updated_at

Possible workflow states:

```text
DRAFT
ACTIVE
INACTIVE
ARCHIVED
```

Use enums rather than scattered string literals.

---

# 9. WORKFLOW VERSIONING

Workflow versions are immutable once published.

Example:

```text
Daily Instagram Workflow

v1
v2
v3
v4 ← active
```

When a user changes a workflow:

```text
DO NOT modify v4
```

Create:

```text
v5
```

Existing executions must continue using the workflow version with which they started.

Never silently execute a historical workflow using the newest definition.

---

# 10. WORKFLOW GRAPH

A workflow is a directed graph.

Example:

```text
Schedule
   ↓
AI Text
   ↓
AI Image
   ↓
Instagram
```

Branches:

```text
             ┌── Instagram
             │
AI Content ──┤
             │
             └── WhatsApp
```

Conditional:

```text
             ┌── TRUE → Instagram
IF ──────────┤
             └── FALSE → Email
```

The engine must NOT assume workflows are always linear.

---

# 11. GRAPH VALIDATION

Before activation or execution, validate:

* node IDs
* node types
* node versions
* duplicate node IDs
* invalid edges
* missing source nodes
* missing target nodes
* cycles
* unreachable nodes
* missing required inputs
* invalid node configuration
* invalid expressions

The validator must return structured errors.

Example:

```json
{
  "valid": false,
  "errors": [
    {
      "node_id": "node_3",
      "code": "MISSING_INPUT",
      "message": "Image input is required"
    }
  ]
}
```

---

# 12. NODE ARCHITECTURE

Every node must follow a small, clear contract.

Conceptually:

```python
class BaseNode:
    type: str
    version: int
    metadata: NodeMetadata

    async def execute(
        self,
        context: ExecutionContext,
        input_data: dict
    ) -> NodeResult:
        ...
```

Use composition where practical.

Do not create deep inheritance hierarchies.

---

# 13. NODE REGISTRY

Create a central registry.

Required capabilities:

```text
register()
get()
exists()
list()
```

Example:

```python
registry.register(MyNode)
node = registry.get("utility.set")
```

The workflow engine should resolve nodes through the registry.

Never hardcode integration types into the engine.

---

# 14. NODE TYPES

The architecture should eventually support:

## Trigger

```text
trigger.manual
trigger.schedule
trigger.webhook
```

## Logic

```text
logic.if
logic.switch
logic.filter
logic.loop
logic.merge
logic.wait
logic.stop
```

## Transform

```text
transform.set
transform.map
transform.json
transform.text
transform.date
transform.math
```

## AI

```text
ai.generate_text
ai.generate_image
ai.classify
ai.extract_json
ai.summarize
ai.agent
```

## Communication

```text
email.send
whatsapp.send
telegram.send
slack.send
sms.send
```

## Social

```text
instagram.publish
facebook.publish
linkedin.publish
youtube.publish
```

## Data

```text
postgres.query
mysql.query
google_sheets.read
google_sheets.write
```

## Utility

```text
http.request
utility.log
utility.delay
```

Do not implement every node immediately.

Build the framework first.

---

# 15. NODE METADATA

Every node should expose machine-readable metadata.

Example:

```json
{
  "type": "email.send",
  "version": 1,
  "name": "Send Email",
  "description": "Send an email",
  "category": "communication",
  "inputs": [],
  "outputs": [],
  "config_schema": {}
}
```

The future frontend will consume this metadata to build configuration forms.

Do not put frontend-specific rendering logic into the node implementation.

---

# 16. CONFIGURATION SCHEMAS

Node configuration must be validated using Pydantic or an equivalent typed mechanism.

Example:

```text
Email Send

to       required string
subject  required string
body     required string
```

The node must fail validation before execution if configuration is invalid.

---

# 17. EXECUTION CONTEXT

Every workflow execution gets an isolated context.

Conceptually:

```python
ExecutionContext(
    execution_id,
    workflow_id,
    workflow_version_id,
    variables,
    node_results,
    metadata
)
```

Never use global mutable execution state.

Every execution must be isolated from every other execution.

---

# 18. VARIABLE SYSTEM

Support references such as:

```text
{{trigger.data}}
{{node_1.output}}
{{node_1.output.email}}
{{workflow.variables.topic}}
{{execution.id}}
```

Variables should be resolved through a dedicated expression/variable resolver.

Do NOT use Python `eval()`.

Expressions must be safely parsed and evaluated.

---

# 19. INPUT RESOLUTION

Node configuration can contain dynamic variables.

Example:

```json
{
  "message": "Hello {{customer.name}}"
}
```

The engine resolves it before node execution.

Resolution must work recursively for:

* strings
* dictionaries
* arrays
* nested objects

---

# 20. EXECUTION ENGINE

The execution engine is responsible for:

* loading workflow version
* validating graph
* creating execution context
* resolving dependencies
* selecting executable nodes
* executing nodes
* storing node outputs
* handling branches
* handling failures
* handling retries
* updating execution state
* supporting resume/cancellation

It must NOT contain integration-specific code.

---

# 21. NODE EXECUTION

Every node execution must have:

```text
PENDING
RUNNING
SUCCESS
FAILED
SKIPPED
WAITING
RETRYING
CANCELLED
TIMEOUT
```

Workflow execution:

```text
PENDING
RUNNING
WAITING
SUCCESS
FAILED
CANCELLED
TIMEOUT
```

Use enums.

---

# 22. EXECUTION PERSISTENCE

Persist workflow execution history.

Each execution should contain:

```text
execution_id
workflow_id
workflow_version_id
status
started_at
finished_at
duration
trigger_data
error
```

Each node execution should contain:

```text
execution_id
node_id
node_type
status
input
output
error
retry_count
started_at
finished_at
duration
```

Sensitive values must be redacted.

---

# 23. QUEUE / WORKER

Long-running workflow execution must not block API requests.

Architecture:

```text
API
 ↓
Create Execution
 ↓
Queue
 ↓
Worker
 ↓
Workflow Engine
 ↓
Node
```

The API should return an execution ID.

Example:

```http
POST /api/v1/workflows/{id}/execute
```

Response:

```json
{
  "execution_id": "exec_123",
  "status": "PENDING"
}
```

---

# 24. REDIS

Use Redis for:

* queue infrastructure
* transient execution coordination
* scheduling support where appropriate
* caching where useful

Do not use Redis as the primary source of truth for workflow definitions or execution history.

PostgreSQL remains the durable source of truth.

---

# 25. RETRY

Retries must be configurable.

Example:

```json
{
  "retry": {
    "enabled": true,
    "max_attempts": 3,
    "backoff_seconds": 10
  }
}
```

Prefer exponential backoff.

Do not retry permanent errors blindly.

Create a retry policy abstraction.

---

# 26. TIMEOUT

Nodes should support configurable timeouts.

On timeout:

1. terminate/cancel where possible
2. record timeout
3. apply retry policy
4. update execution state

Never leave an execution permanently stuck without a persisted state.

---

# 27. WAITING / DELAY

Long delays must not hold a worker process.

Bad:

```python
await asyncio.sleep(3600)
```

for a one-hour workflow delay.

Instead:

```text
RUNNING
   ↓
WAITING
   ↓
persist resume time
   ↓
worker released
   ↓
scheduler/queue
   ↓
resume execution
```

Design the system so long-running workflows are resumable.

---

# 28. CANCELLATION

Support cancellation.

Example:

```http
POST /api/v1/executions/{id}/cancel
```

The execution engine must check cancellation state between nodes and during long-running operations where possible.

---

# 29. IDEMPOTENCY

Workflow executions and external side effects must consider idempotency.

Example:

```text
Worker executes Instagram Publish
Instagram succeeds
Worker crashes before DB update
Worker retries
```

Without protection, duplicate posts may occur.

Design node-level idempotency support.

Use:

```text
execution_id
node_id
attempt
idempotency_key
```

where appropriate.

Document limitations because external APIs may not provide true idempotency.

---

# 30. TRIGGERS

Triggers must also be modular.

Create a trigger abstraction.

Initial triggers:

```text
Manual
Schedule
Webhook
```

Future triggers:

```text
Email
Database event
External event
Queue event
```

Normalize trigger input into the workflow execution context.

---

# 31. SCHEDULER

Scheduled workflows must support:

```text
cron
timezone
enabled/disabled
next_run
```

Example:

```json
{
  "type": "schedule",
  "cron": "0 10 * * *",
  "timezone": "Asia/Kolkata"
}
```

Do not put scheduling logic inside individual nodes.

---

# 32. WEBHOOKS

Webhook execution should follow:

```text
HTTP Request
 ↓
Validate
 ↓
Create Execution
 ↓
Queue
 ↓
Return execution ID
```

Do not run arbitrary workflows synchronously inside the webhook request.

Protect webhooks against abuse.

---

# 33. HTTP REQUEST NODE

The HTTP node should support:

```text
GET
POST
PUT
PATCH
DELETE
headers
query parameters
body
authentication
timeout
```

Dynamic variables should be supported.

Example:

```json
{
  "url": "{{config.api_url}}",
  "body": {
    "name": "{{customer.name}}"
  }
}
```

The HTTP node must include SSRF protection.

Do not allow unrestricted access to internal/private network resources.

---

# 34. IF NODE

The IF node should support conditions such as:

```text
equals
not_equals
contains
starts_with
ends_with
greater_than
less_than
greater_than_or_equal
less_than_or_equal
exists
not_exists
```

Example:

```text
{{customer.age}} > 18
```

The node should expose branch outputs:

```text
true
false
```

---

# 35. LOOP DESIGN

Loops may be implemented later.

However, the graph/execution architecture must not make loops impossible.

Future support:

```text
for_each
batch
iteration_context
item_index
```

Avoid assuming that every node executes exactly once per workflow execution.

---

# 36. CREDENTIALS

Credentials must be completely separate from workflow definitions.

Bad:

```json
{
  "access_token": "secret"
}
```

inside workflow JSON.

Correct:

```json
{
  "credential_id": "cred_123"
}
```

Credential storage must support encryption at rest.

Never expose credentials through API responses.

Never log secrets.

---

# 37. MULTI-TENANCY

Design for SaaS.

Use:

```text
workspace_id
```

or:

```text
tenant_id
```

where appropriate.

All workspace-owned resources must enforce tenant isolation.

A workspace must never be able to access another workspace's:

* workflows
* versions
* executions
* credentials
* schedules
* webhooks

Do not rely on frontend filtering.

---

# 38. API DESIGN

Use versioned APIs:

```text
/api/v1
```

Example:

```text
POST   /api/v1/workflows
GET    /api/v1/workflows
GET    /api/v1/workflows/{id}
PUT    /api/v1/workflows/{id}
DELETE /api/v1/workflows/{id}

POST   /api/v1/workflows/{id}/validate
POST   /api/v1/workflows/{id}/execute

GET    /api/v1/workflows/{id}/versions
POST   /api/v1/workflows/{id}/versions

GET    /api/v1/executions
GET    /api/v1/executions/{id}
GET    /api/v1/executions/{id}/nodes
POST   /api/v1/executions/{id}/cancel

GET    /api/v1/nodes

GET    /api/v1/credentials
POST   /api/v1/credentials

GET    /api/v1/schedules
POST   /api/v1/schedules
```

Do not expose database models directly.

Use Pydantic request/response schemas.

---

# 39. API LAYER

API routes should be thin.

Preferred:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Database
```

Do not put complex business logic inside route functions.

---

# 40. DATABASE LAYER

Use:

* SQLAlchemy 2.x
* Alembic
* PostgreSQL

Recommended entities:

```text
workspaces
users
workflows
workflow_versions
workflow_executions
node_executions
credentials
schedules
webhooks
```

Use JSONB where flexible workflow/node data is appropriate.

Do not put the entire application's relational model into one giant JSON document.

---

# 41. TRANSACTIONS

Think carefully about transaction boundaries.

For example:

Creating an execution and scheduling it for processing should be reliable.

Document any unavoidable distributed transaction boundaries between:

```text
PostgreSQL
Redis
Worker
External APIs
```

Do not pretend distributed operations are atomic when they are not.

---

# 42. SECURITY

Security is a first-class requirement.

Always:

* validate input
* use parameterized queries
* encrypt credentials
* redact secrets
* isolate tenants
* validate webhooks
* protect against SSRF
* prevent unsafe expression execution
* apply rate limits
* limit request sizes
* avoid secrets in logs
* avoid secrets in errors
* validate external URLs
* validate uploaded content where applicable

Never use:

```python
eval(user_input)
```

Never execute arbitrary user Python code in the main application process.

If a future Code node is implemented, it requires a proper sandbox architecture.

---

# 43. OBSERVABILITY

Use structured logging.

Every important operation should include:

```text
execution_id
workflow_id
workflow_version_id
node_id
node_type
```

Prepare architecture for:

* metrics
* tracing
* OpenTelemetry
* Prometheus

Do not over-engineer observability during MVP.

---

# 44. TESTING

Every important feature requires tests.

## Unit tests

Test:

* graph validation
* cycle detection
* topological ordering
* expression resolution
* variable substitution
* node registry
* retry policy
* timeout policy
* condition evaluation
* configuration validation

## Integration tests

Test:

* PostgreSQL
* Redis
* workflow persistence
* execution persistence
* worker execution
* queue processing
* webhook trigger
* scheduler

## E2E

Example:

```text
Manual Trigger
 ↓
Set
 ↓
IF
 ↓
Log
```

Verify:

```text
workflow created
workflow validated
execution created
worker receives job
nodes execute
outputs propagate
execution becomes SUCCESS
```

Also test failure scenarios.

---

# 45. FAILURE TESTING

Explicitly test:

* node failure
* retry
* retry exhaustion
* timeout
* cancellation
* invalid workflow
* invalid node
* missing credential
* external API failure
* worker crash
* duplicate execution
* database failure
* Redis failure

A workflow engine is defined as much by its failure behavior as its success behavior.

---

# 46. CODE QUALITY

Follow these rules:

### DO

* use type hints
* use clear names
* keep functions focused
* keep classes focused
* use dependency injection where useful
* use async where appropriate
* write tests
* document important architectural decisions
* prefer composition
* keep modules independent

### DON'T

* create giant files
* create giant classes
* duplicate execution logic
* hardcode integrations into the engine
* put DB queries inside nodes
* put business logic inside API routes
* use global mutable state
* use unsafe eval
* hardcode secrets
* create unnecessary abstractions
* create premature microservices

---

# 47. ERROR HANDLING

Create structured application errors.

Examples:

```text
WorkflowValidationError
NodeConfigurationError
NodeExecutionError
CredentialError
AuthenticationError
AuthorizationError
ExternalAPIError
RateLimitError
NodeTimeoutError
ExecutionCancelledError
```

Map them to appropriate API responses.

Do not leak internal implementation details to users.

---

# 48. LOGGING RULES

Never log:

```text
password
access_token
refresh_token
api_key
client_secret
authorization header
credential data
```

Use redaction utilities.

Example:

```text
Authorization: [REDACTED]
```

---

# 49. DATABASE MIGRATIONS

Every schema change must use Alembic.

Never modify production database structure manually.

Development workflow:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Review generated migrations before applying them.

---

# 50. ENVIRONMENT CONFIGURATION

Use environment variables.

Example:

```text
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
ENCRYPTION_KEY=
LOG_LEVEL=
ENVIRONMENT=
```

Provide:

```text
.env.example
```

Never commit real credentials.

---

# 51. DOCKER

Provide Docker Compose for local infrastructure.

At minimum:

```text
api
postgres
redis
worker
```

Scheduler may be a separate process if useful.

Keep local development simple.

---

# 52. DEVELOPMENT COMMANDS

The project should eventually support commands similar to:

```bash
docker compose up -d

uvicorn app.main:app --reload

pytest

alembic upgrade head
```

Document the actual commands in README.md.

---

# 53. NODE DEVELOPMENT RULE

Adding a new node should be easy.

A developer should ideally only need to:

```text
1. Create node implementation
2. Define configuration schema
3. Define metadata
4. Register node
5. Add tests
```

They should NOT have to modify:

```text
WorkflowEngine
GraphExecutor
ExecutionContext
```

unless the feature introduces genuinely new core execution semantics.

---

# 54. INTEGRATION ARCHITECTURE

External APIs must be isolated.

Example:

```text
integrations/
    instagram/
        client.py
        auth.py
        nodes.py
        schemas.py
        exceptions.py

    whatsapp/
        client.py
        auth.py
        nodes.py
        schemas.py
        exceptions.py

    email/
        client.py
        auth.py
        nodes.py
        schemas.py
        exceptions.py
```

Separate:

```text
API client
```

from:

```text
Workflow node
```

Example:

```text
InstagramPublishNode
        ↓
InstagramClient
        ↓
Instagram API
```

The node should translate workflow input into integration-client calls.

---

# 55. INTEGRATION ERROR NORMALIZATION

External providers have different error formats.

Normalize them into internal categories:

```text
AUTHENTICATION
AUTHORIZATION
RATE_LIMIT
VALIDATION
NETWORK
TIMEOUT
NOT_FOUND
PROVIDER_ERROR
```

The core engine should operate on normalized errors.

---

# 56. API CLIENT RULES

External API clients must handle:

* timeouts
* retries where appropriate
* rate limits
* authentication
* structured errors
* request logging without secrets

Do not blindly retry every HTTP status.

---

# 57. FUTURE FRONTEND CONTRACT

Although frontend is not currently part of this project, backend APIs must be designed with the future visual workflow editor in mind.

The future UI will need:

```text
Node list
Node metadata
Node configuration schema
Workflow definition
Workflow validation
Execution status
Execution node status
Execution logs
```

Therefore provide clean APIs for these capabilities.

---

# 58. EXECUTION API

The future UI should be able to display:

```text
Workflow
   ↓
Execution
   ↓
Node 1 ✓
   ↓
Node 2 ✓
   ↓
Node 3 ✕
```

The backend must expose sufficient execution information to render this without accessing the database directly.

---

# 59. DOCUMENTATION

Maintain:

```text
README.md
ARCHITECTURE.md
API.md
DATABASE.md
SECURITY.md
TESTING.md
NODE_DEVELOPMENT.md
```

When architecture changes significantly, update documentation.

Do not allow documentation to become misleading.

---

# 60. IMPLEMENTATION STRATEGY

Do not implement the entire platform in one step.

Work incrementally.

Recommended order:

```text
PHASE 1
Project foundation

PHASE 2
Database/domain models

PHASE 3
Workflow definition

PHASE 4
Graph validation

PHASE 5
Node system + registry

PHASE 6
Execution context

PHASE 7
Execution engine

PHASE 8
Expression system

PHASE 9
MVP nodes

PHASE 10
Redis + worker

PHASE 11
Retries/timeouts/cancellation

PHASE 12
Triggers

PHASE 13
Credentials

PHASE 14
Scheduler

PHASE 15
Webhook

PHASE 16
Integration framework

PHASE 17
Instagram/WhatsApp/Email

PHASE 18
Hardening/security/observability
```

---

# 61. AGENT WORKFLOW

Before modifying code:

1. Inspect the repository.
2. Understand the current architecture.
3. Identify affected modules.
4. Check existing tests.
5. Check existing documentation.
6. Create a concise implementation plan.

Before writing code:

```text
Understand
 ↓
Plan
 ↓
Implement
 ↓
Test
 ↓
Review
 ↓
Fix
 ↓
Document
```

Do not blindly overwrite existing code.

---

# 62. CHANGE DISCIPLINE

For every feature:

1. Make the smallest reasonable change.
2. Avoid unrelated refactoring.
3. Preserve existing behavior.
4. Add tests.
5. Run relevant tests.
6. Run lint/type checks where configured.
7. Review security implications.
8. Update documentation if architecture changed.

---

# 63. NEVER FAKE SUCCESS

Never claim:

```text
implemented
tested
working
verified
```

unless the code was actually inspected/run/tested.

If something cannot be tested, explicitly state what was not verified.

Do not invent test results.

---

# 64. WHEN SOMETHING FAILS

When a test/build/runtime error occurs:

1. Read the complete error.
2. Identify the root cause.
3. Fix the root cause.
4. Re-run the failing test.
5. Run related tests.
6. Check for regressions.

Do not randomly change multiple unrelated files to make an error disappear.

---

# 65. ARCHITECTURAL REVIEW QUESTIONS

Before adding a major feature, ask:

1. Does this belong in the core engine?
2. Can this be implemented as a node?
3. Does this introduce integration-specific logic into the core?
4. Does this break workflow versioning?
5. Does this work with asynchronous execution?
6. Does this work with retries?
7. Does this work with cancellation?
8. Does this work with multiple tenants?
9. Does this expose secrets?
10. Does this introduce concurrency problems?
11. Does this require persistence?
12. Can this be tested independently?

---

# 66. CORE VS NODE DECISION

Use this rule:

If a feature changes HOW workflows execute:

```text
graph
branching
retry
timeout
waiting
execution state
context
scheduling
```

it probably belongs in the CORE.

If a feature changes WHAT a workflow can DO:

```text
Instagram
WhatsApp
Email
Slack
Google Sheets
OpenAI
HTTP API
```

it probably belongs in a NODE/INTEGRATION.

---

# 67. PERFORMANCE

Do not optimize prematurely.

First prioritize:

```text
correctness
reliability
maintainability
observability
```

Then optimize bottlenecks based on measurements.

Avoid:

* N+1 queries
* unnecessary DB queries
* blocking async event loops
* unbounded queue growth
* loading huge workflow execution payloads unnecessarily
* storing huge binary files directly in PostgreSQL

---

# 68. FILE/BINARY DATA

The workflow engine may eventually process:

* images
* videos
* PDFs
* CSVs

Do not assume PostgreSQL is the correct storage for large binary objects.

Design an abstraction for object/file storage so future storage providers can be added.

Example:

```text
StorageService
    ↓
LocalStorage
S3Storage
MinIOStorage
```

Do not implement all providers unless required.

---

# 69. FUTURE SCALE

The architecture should eventually support:

```text
multiple workers
multiple scheduler instances
horizontal API scaling
distributed execution
large workflow counts
large execution counts
concurrent executions
rate-limited integrations
```

Do not prematurely implement distributed complexity.

Design clean boundaries so scaling can be added later.

---

# 70. CURRENT MVP DEFINITION

The first complete backend MVP should be capable of executing:

```text
Manual Trigger
      ↓
Set
      ↓
IF
   ┌──┴──┐
 TRUE   FALSE
  ↓       ↓
Log     Log
```

And:

```text
Manual Trigger
      ↓
HTTP Request
      ↓
Set
      ↓
Log
```

The system must persist:

* workflow
* workflow version
* execution
* node executions
* node outputs
* errors
* status

---

# 71. FIRST DEVELOPMENT TASK

When starting from an empty repository:

Implement ONLY:

```text
PHASE 1
```

Phase 1 includes:

* Python project
* FastAPI
* configuration
* PostgreSQL
* SQLAlchemy
* Alembic
* Redis
* structured logging
* health endpoints
* Docker Compose
* pytest setup
* basic project structure

Health endpoints:

```text
GET /health
GET /health/db
GET /health/redis
```

Do NOT implement:

* workflow engine
* nodes
* Instagram
* WhatsApp
* Email
* scheduler
* workflow UI

until Phase 1 is complete.

---

# 72. PHASE COMPLETION RULE

After completing a phase:

1. Show files changed.
2. Explain architecture changes.
3. Run tests.
4. Report actual test results.
5. Identify known limitations.
6. Update documentation.

Then STOP.

Do not automatically continue to the next phase.

Wait for explicit instruction:

```text
CONTINUE PHASE 2
```

---

# 73. FINAL PRINCIPLE

Always remember:

```text
The engine executes workflows.

Nodes provide capabilities.

Integrations communicate with external systems.

The database stores durable state.

Redis/queues coordinate asynchronous work.

The API exposes the platform.

The future frontend visualizes and edits workflows.
```

Keep these responsibilities separate.

The long-term goal is to make adding:

```text
1 integration
10 integrations
100 integrations
500 integrations
```

possible without rewriting the workflow engine.

Build for clarity first.

Build for extensibility second.

Build for scale third.

Do not sacrifice simplicity for theoretical scalability.
