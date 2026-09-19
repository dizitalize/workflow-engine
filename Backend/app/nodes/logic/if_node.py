from typing import Any
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult


class IfNode(BaseNode):
    metadata = NodeMetadata(
        type="logic.if",
        version=1,
        name="IF",
        description="Conditional branching based on comparison",
        category="logic",
        config_schema={
            "type": "object",
            "properties": {
                "left": {},
                "operator": {"type": "string", "enum": ["equals", "not_equals", "contains", "greater_than", "less_than", "exists", "not_exists"]},
                "right": {},
            },
            "required": ["left", "operator"],
        },
        outputs=[
            {"name": "true", "description": "True branch"},
            {"name": "false", "description": "False branch"},
        ],
    )

    OPERATORS = {
        "equals": lambda l, r: l == r,
        "not_equals": lambda l, r: l != r,
        "contains": lambda l, r: r in l if isinstance(l, (str, list, dict)) else False,
        "greater_than": lambda l, r: l > r,
        "less_than": lambda l, r: l < r,
        "exists": lambda l, r: l is not None and l != "",
        "not_exists": lambda l, r: l is None or l == "",
    }

    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        left = input_data.get("left")
        operator = input_data.get("operator")
        right = input_data.get("right")

        op_func = self.OPERATORS.get(operator)
        if not op_func:
            return NodeResult(
                output=None,
                error=f"Unknown operator: {operator}",
                success=False,
            )

        try:
            result = op_func(left, right)
        except Exception as e:
            return NodeResult(
                output=None,
                error=f"Comparison error: {str(e)}",
                success=False,
            )

        return NodeResult(
            output={"result": result, "branch": "true" if result else "false"},
            success=True,
        )