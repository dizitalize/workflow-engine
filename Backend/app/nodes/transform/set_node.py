from typing import Any
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult


class SetNode(BaseNode):
    metadata = NodeMetadata(
        type="transform.set",
        version=1,
        name="Set",
        description="Create or modify workflow data",
        category="transform",
        config_schema={
            "type": "object",
            "properties": {
                "values": {"type": "object"}
            },
            "required": ["values"],
        },
    )

    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        values = input_data.get("values", {})
        return NodeResult(output=values, success=True)