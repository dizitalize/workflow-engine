import logging
from typing import Any
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult


logger = logging.getLogger(__name__)


class LogNode(BaseNode):
    metadata = NodeMetadata(
        type="utility.log",
        version=1,
        name="Log",
        description="Log data to console and pass through",
        category="utility",
        config_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
            },
        },
    )

    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        message = input_data.get("message", "")
        logger.info(f"[LOG] {message}")
        return NodeResult(output={"message": message}, success=True)