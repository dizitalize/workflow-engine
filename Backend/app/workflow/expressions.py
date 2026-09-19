import re
from typing import Any


class ExpressionResolver:
    VARIABLE_PATTERN = re.compile(r"^\{\{([^}]+)\}\}$")
    VARIABLE_IN_TEXT_PATTERN = re.compile(r"\{\{([^}]+)\}\}")

    def __init__(self, context: dict[str, Any]):
        self.context = context

    def resolve(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._resolve_string(value)
        elif isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.resolve(item) for item in value]
        return value

    def _resolve_string(self, text: str) -> Any:
        # Check if the entire string is a single variable reference
        match = self.VARIABLE_PATTERN.match(text.strip())
        if match:
            path = match.group(1).strip()
            result = self._get_value(path)
            if result is not None:
                return result
            return text

        # Otherwise, replace variables within the text
        def replace_var(match: re.Match) -> str:
            path = match.group(1).strip()
            result = self._get_value(path)
            if result is None:
                return match.group(0)
            return str(result)

        resolved = self.VARIABLE_IN_TEXT_PATTERN.sub(replace_var, text)

        if resolved == text:
            return text

        if self.VARIABLE_IN_TEXT_PATTERN.search(resolved):
            return self._resolve_string(resolved)

        return resolved

    def _get_value(self, path: str) -> Any:
        parts = path.split(".")
        current: Any = self.context

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None

            if current is None:
                return None

        return current


def resolve_variables(value: Any, context: dict[str, Any]) -> Any:
    resolver = ExpressionResolver(context)
    return resolver.resolve(value)