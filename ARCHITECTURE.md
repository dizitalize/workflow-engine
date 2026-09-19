# Architecture

## Overview

This document describes the architecture of the Workflow Engine local MVP.

## Core Components

### 1. API Layer
FastAPI routes that handle HTTP requests. Thin layer that delegates to services.

### 2. Service Layer
Business logic layer:
- `WorkflowService` - Workflow CRUD, validation
- `WorkflowVersionService` - Version management
- `ExecutionService` - Workflow execution

### 3. Repository Layer
Data access layer using SQLAlchemy:
- `WorkflowRepository`
- `WorkflowVersionRepository`
- `ExecutionRepository`

### 4. Workflow Engine
Core execution logic:
- `GraphExecutor` - Executes workflow graph
- `ExecutionContext` - Isolated execution context
- `GraphValidator` - Validates workflow before execution
- `ExpressionResolver` - Resolves variables in configurations

### 5. Node System
Pluggable node architecture:
- `BaseNode` - Abstract base class
- `NodeRegistry` - Central registry for node types
- `NodeMetadata` - Node description for frontend

## Data Flow

```
HTTP Request
    ↓
API Route
    ↓
Service
    ↓
Repository → Database
    ↓
Workflow Engine
    ↓
Graph Validator
    ↓
Graph Executor
    ↓
Node Registry → Node Instance
    ↓
Node.execute(context, input)
    ↓
Store Results
```

## Database Schema

```
workflows
  - id (PK)
  - name
  - description
  - status (DRAFT, ACTIVE, INACTIVE)
  - active_version_id (FK)
  - created_at
  - updated_at

workflow_versions
  - id (PK)
  - workflow_id (FK)
  - version
  - definition (JSON)
  - created_at

workflow_executions
  - id (PK)
  - workflow_id (FK)
  - version_id (FK)
  - status (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
  - trigger_data (JSON)
  - output (JSON)
  - error
  - started_at
  - finished_at

node_executions
  - id (PK)
  - execution_id (FK)
  - node_id
  - node_type
  - status (PENDING, RUNNING, SUCCESS, FAILED, SKIPPED)
  - input (JSON)
  - output (JSON)
  - error
  - retry_count
  - started_at
  - finished_at
```

## Execution Model

1. **Workflow Definition** - JSON with nodes and edges
2. **Graph Building** - Build adjacency lists from edges
3. **Validation** - Check cycles, unreachable nodes, config
4. **Context Creation** - Isolated ExecutionContext per execution
5. **Topological Execution** - Execute nodes in dependency order
6. **Variable Resolution** - Resolve `{{variables}}` before each node
7. **Branch Handling** - IF node selects true/false branch
8. **Persistence** - Store execution and node execution records

## Key Design Decisions

### Node Registry Pattern
Nodes are registered in a central registry. The engine never knows about specific node types.

### Expression Resolution
Safe variable resolution without `eval()`. Supports nested objects, arrays, and recursive resolution.

### Synchronous Execution (MVP)
For local MVP, execution happens in the API request. Architecture supports async workers later.

### Version Immutability
Workflow versions are immutable once created. New versions created on changes.

## Future Migration Path

```
SQLite → PostgreSQL
Sync → Async (Redis + Workers)
Local → Multi-tenant
```