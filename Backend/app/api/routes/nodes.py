from fastapi import APIRouter
from Backend.app.workflow.registry import registry

router = APIRouter(prefix="/api/v1/nodes", tags=["nodes"])


@router.get("")
async def list_nodes():
    nodes = registry.list()
    return [
        {
            "type": node.type,
            "version": node.version,
            "name": node.name,
            "description": node.description,
            "category": node.category,
            "inputs": node.inputs,
            "outputs": node.outputs,
            "config_schema": node.config_schema,
        }
        for node in nodes
    ]