from typing import Any
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult


class ManualTriggerNode(BaseNode):
    metadata = NodeMetadata(
        type="trigger.manual",
        version=1,
        name="Manual Trigger",
        description="Start a workflow manually with input data",
        category="trigger",
        config_schema={},
    )

    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        return NodeResult(output=context.trigger_data, success=True)