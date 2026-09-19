import httpx
from typing import Any
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult


class HttpRequestNode(BaseNode):
    metadata = NodeMetadata(
        type="utility.http_request",
        version=1,
        name="HTTP Request",
        description="Make HTTP requests",
        category="utility",
        config_schema={
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                "url": {"type": "string", "format": "uri"},
                "headers": {"type": "object"},
                "params": {"type": "object"},
                "body": {},
                "timeout": {"type": "number", "default": 30},
            },
            "required": ["method", "url"],
        },
    )

    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        method = input_data.get("method", "GET").upper()
        url = input_data.get("url", "")
        headers = input_data.get("headers", {})
        params = input_data.get("params", {})
        body = input_data.get("body")
        timeout = input_data.get("timeout", 30)

        if not url:
            return NodeResult(output=None, error="URL is required", success=False)

        allowed_schemes = ["http", "https"]
        if not any(url.startswith(scheme + "://") for scheme in allowed_schemes):
            return NodeResult(output=None, error="Only HTTP/HTTPS URLs are allowed", success=False)

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=body if body is not None else None,
                )

                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text

                return NodeResult(
                    output={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": response_data,
                    },
                    success=True,
                )

        except httpx.TimeoutException:
            return NodeResult(output=None, error="Request timeout", success=False)
        except httpx.RequestError as e:
            return NodeResult(output=None, error=f"Request failed: {str(e)}", success=False)
        except Exception as e:
            return NodeResult(output=None, error=f"Unexpected error: {str(e)}", success=False)