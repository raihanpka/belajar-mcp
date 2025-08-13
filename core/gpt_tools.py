import json
from typing import Optional, Literal, List
from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionToolMessageParam,
)

class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[Tool]:
        """Gets all tools from the provided clients."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema,
                    }
                }
                for t in tool_models
            ]
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    def _build_tool_result_part(
        cls,
        tool_use_id: str,
        text: str,
        status: Literal["success"] | Literal["error"],
    ) -> ChatCompletionToolMessageParam:
        """Builds a tool result message for OpenAI."""
        return {
            "role": "tool",
            "tool_call_id": tool_use_id,
            "content": text,
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], message: dict
    ) -> List[ChatCompletionToolMessageParam]:
        """Executes a list of tool requests against the provided clients."""
        tool_requests = message.get("tool_calls", [])
        tool_result_blocks: list[ChatCompletionToolMessageParam] = []

        for tool_request in tool_requests:
            tool_use_id = tool_request.get("id", "")
            tool_name = tool_request.get("function", {}).get("name", "")
            tool_input_str = tool_request.get("function", {}).get("arguments", "{}")
            
            try:
                tool_input = json.loads(tool_input_str) if tool_input_str else {}
            except json.JSONDecodeError:
                tool_result_blocks.append(
                    cls._build_tool_result_part(
                        tool_use_id,
                        json.dumps({"error": "Invalid JSON in tool arguments"}),
                        "error",
                    )
                )
                continue

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_result_blocks.append(
                    cls._build_tool_result_part(
                        tool_use_id, "Could not find that tool", "error"
                    )
                )
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                items = []
                if tool_output:
                    items = tool_output.content
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                content_json = json.dumps(content_list)
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id,
                    content_json,
                    "error"
                    if tool_output and tool_output.isError
                    else "success",
                )
            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id,
                    json.dumps({"error": error_message}),
                    "error",
                )

            tool_result_blocks.append(tool_result_part)
        return tool_result_blocks
