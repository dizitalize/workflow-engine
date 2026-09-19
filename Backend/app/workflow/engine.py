from typing import Any
from datetime import datetime
from uuid import uuid4

from Backend.app.db.database import get_session
from Backend.app.db.models import WorkflowExecution, NodeExecution, ExecutionStatus, NodeExecutionStatus
from Backend.app.workflow.graph import WorkflowGraph
from Backend.app.workflow.registry import registry
from Backend.app.workflow.context import ExecutionContext, ExecutionCancelledError
from Backend.app.workflow.expressions import resolve_variables
from Backend.app.schemas.node import NodeDefinition, EdgeDefinition


class GraphExecutor:
    def __init__(self, graph: WorkflowGraph):
        self.graph = graph

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        context.workflow_id = context.workflow_id
        context.workflow_version_id = context.workflow_version_id

        trigger_nodes = self.graph.get_trigger_nodes()
        
        for trigger in trigger_nodes:
            context.current_node_id = trigger.id
            await self._execute_node(trigger, context)

        return context.node_results

    async def _execute_node(self, node_def: NodeDefinition, context: ExecutionContext) -> None:
        node_class = registry.get(node_def.type)
        if not node_class:
            raise ValueError(f"Node type not registered: {node_def.type}")

        node_instance = node_class()
        context.current_node_id = node_def.id

        await self._record_node_start(context, node_def, node_instance.metadata.type)

        try:
            resolved_config = resolve_variables(node_def.config, self._build_resolution_context(context))

            context.check_cancellation()

            node_instance.metadata  # just to access
            result = await node_instance.execute(context, resolved_config)

            if not result.success:
                await self._record_node_failure(context, node_def, result.error)
                context.node_results[node_def.id] = {"error": result.error}
                raise Exception(f"Node {node_def.id} failed: {result.error}")

            context.set_node_result(node_def.id, result.output)
            await self._record_node_success(context, node_def, result.output)

            # Handle branching for IF node
            await self._handle_branching(node_def, result.output, context)

        except ExecutionCancelledError:
            await self._record_node_cancelled(context, node_def)
            raise
        except Exception as e:
            await self._record_node_failure(context, node_def, str(e))
            raise

    async def _handle_branching(self, node_def: NodeDefinition, output: Any, context: ExecutionContext) -> None:
        """Handle branching logic for nodes that produce branch output"""
        # Check if this is an IF node with branch output
        if (isinstance(output, dict) and 
            "branch" in output and 
            node_def.type == "logic.if"):
            
            branch = output["branch"]  # "true" or "false"
            edges = self.graph.get_next_edges(node_def.id)
            
            # Track which branches we've executed
            executed_branches = set()
            
            # Execute matching branches
            for edge in edges:
                if edge.source_handle == branch:
                    node = self.graph.get_node(edge.target)
                    if node:
                        executed_branches.add(edge.source_handle)
                        await self._execute_node(node, context)
            
            # Mark non-matching branches as SKIPPED
            for edge in edges:
                if edge.source_handle not in executed_branches:
                    node = self.graph.get_node(edge.target)
                    if node:
                        await self._record_node_skipped(context, node)
        else:
            # Normal execution - execute all next nodes
            for next_node in self.graph.get_next_nodes(node_def.id):
                await self._execute_node(next_node, context)

    def _build_resolution_context(self, context: ExecutionContext) -> dict[str, Any]:
        return {
            "trigger": context.trigger_data,
            "execution": {"id": context.execution_id},
            "workflow": {"variables": context.variables},
            **context.node_results,
        }

    async def _record_node_start(self, context: ExecutionContext, node_def: NodeDefinition, node_type: str):
        async with get_session() as session:
            node_exec = NodeExecution(
                id=str(uuid4()),
                execution_id=context.execution_id,
                node_id=node_def.id,
                node_type=node_type,
                status=NodeExecutionStatus.RUNNING,
                input=node_def.config,
                started_at=datetime.utcnow(),
            )
            session.add(node_exec)

    async def _record_node_success(self, context: ExecutionContext, node_def: NodeDefinition, output: Any):
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(NodeExecution).where(
                    NodeExecution.execution_id == context.execution_id,
                    NodeExecution.node_id == node_def.id
                )
            )
            node_exec = result.scalar_one_or_none()
            if node_exec:
                node_exec.status = NodeExecutionStatus.SUCCESS
                node_exec.output = output
                node_exec.finished_at = datetime.utcnow()

    async def _record_node_failure(self, context: ExecutionContext, node_def: NodeDefinition, error: str):
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(NodeExecution).where(
                    NodeExecution.execution_id == context.execution_id,
                    NodeExecution.node_id == node_def.id
                )
            )
            node_exec = result.scalar_one_or_none()
            if node_exec:
                node_exec.status = NodeExecutionStatus.FAILED
                node_exec.error = error
                node_exec.finished_at = datetime.utcnow()

    async def _record_node_cancelled(self, context: ExecutionContext, node_def: NodeDefinition):
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(NodeExecution).where(
                    NodeExecution.execution_id == context.execution_id,
                    NodeExecution.node_id == node_def.id
                )
            )
            node_exec = result.scalar_one_or_none()
            if node_exec:
                node_exec.status = NodeExecutionStatus.FAILED
                node_exec.error = "Execution cancelled"
                node_exec.finished_at = datetime.utcnow()


    async def _record_node_skipped(self, context: ExecutionContext, node_def: NodeDefinition):
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(NodeExecution).where(
                    NodeExecution.execution_id == context.execution_id,
                    NodeExecution.node_id == node_def.id
                )
            )
            node_exec = result.scalar_one_or_none()
            if node_exec:
                node_exec.status = NodeExecutionStatus.SKIPPED
                node_exec.finished_at = datetime.utcnow()
            else:
                # Create new skipped node execution record
                node_exec = NodeExecution(
                    id=str(uuid4()),
                    execution_id=context.execution_id,
                    node_id=node_def.id,
                    node_type=node_def.type,
                    status=NodeExecutionStatus.SKIPPED,
                    input=node_def.config,
                    finished_at=datetime.utcnow(),
                )
                session.add(node_exec)


async def execute_workflow(
    workflow_id: str,
    version_id: str,
    definition: dict[str, Any],
    trigger_data: dict[str, Any],
) -> dict[str, Any]:
    execution_id = str(uuid4())

    async with get_session() as session:
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            version_id=version_id,
            status=ExecutionStatus.RUNNING,
            trigger_data=trigger_data,
            started_at=datetime.utcnow(),
        )
        session.add(execution)

    context = ExecutionContext(
        execution_id=execution_id,
        workflow_id=workflow_id,
        workflow_version_id=version_id,
        trigger_data=trigger_data,
    )

    nodes = [NodeDefinition(**n) for n in definition.get("nodes", [])]
    edges = [EdgeDefinition(**e) for e in definition.get("edges", [])]
    graph = WorkflowGraph(nodes=nodes, edges=edges)
    executor = GraphExecutor(graph)

    try:
        output = await executor.execute(context)

        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = result.scalar_one()
            execution.status = ExecutionStatus.SUCCESS
            execution.output = output
            execution.finished_at = datetime.utcnow()

        return {
            "execution_id": execution_id,
            "status": "SUCCESS",
            "output": output,
        }

    except ExecutionCancelledError:
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = result.scalar_one()
            execution.status = ExecutionStatus.CANCELLED
            execution.finished_at = datetime.utcnow()

        return {
            "execution_id": execution_id,
            "status": "CANCELLED",
            "output": None,
        }

    except Exception as e:
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = result.scalar_one()
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.finished_at = datetime.utcnow()

        return {
            "execution_id": execution_id,
            "status": "FAILED",
            "error": str(e),
        }