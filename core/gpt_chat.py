from core.gpt import GPT
from mcp_client import MCPClient
from core.gpt_tools import ToolManager
from openai.types.chat import ChatCompletionMessageParam


class Chat:
    def __init__(self, gpt_service: GPT, clients: dict[str, MCPClient]):
        self.gpt_service: GPT = gpt_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[ChatCompletionMessageParam] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(self, query: str) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            # pastikan chat() di-await (umumnya async)
            raw_resp = self.gpt_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            # --- normalize response: support ChatCompletion (with .choices) or ChatCompletionMessage ---
            if hasattr(raw_resp, "choices"):
                # raw_resp is ChatCompletion
                choice = raw_resp.choices[0]
                finish_reason = getattr(choice, "finish_reason", None)
                message = choice.message  # ChatCompletionMessage object
            else:
                # raw_resp is already ChatCompletionMessage
                message = raw_resp
                finish_reason = getattr(message, "finish_reason", None)

            # Safely extract content
            message_content = getattr(message, "content", "") or ""

            # Build a dict version of message so ToolManager (which expects dict-like) works reliably
            # and so add_assistant_message receives consistent input.
            # Also normalize tool_calls (convert pydantic objects to dicts if needed).
            message_dict = {
                "role": getattr(message, "role", "assistant"),
                "content": message_content,
            }

            raw_tool_calls = getattr(message, "tool_calls", []) or []
            normalized_tool_calls = []
            for tc in raw_tool_calls:
                # Pydantic models usually expose model_dump() in v2
                if hasattr(tc, "model_dump"):
                    try:
                        normalized_tool_calls.append(tc.model_dump())
                        continue
                    except Exception:
                        pass
                # If it's already a dict-like
                if isinstance(tc, dict):
                    normalized_tool_calls.append(tc)
                    continue
                # fallback: try __dict__ or as-is
                try:
                    normalized_tool_calls.append(dict(tc))
                except Exception:
                    normalized_tool_calls.append(tc)
            message_dict["tool_calls"] = normalized_tool_calls

            # Save assistant message (use service helper so it stays consistent with Claude flow)
            # The service's add_assistant_message should accept dict-like messages.
            self.gpt_service.add_assistant_message(self.messages, message_dict)

            # If model requested tool calls (finish_reason or presence of tool_calls)
            if finish_reason == "tool_calls" or normalized_tool_calls:
                print(message_content)
                # Execute tools: ToolManager expects a dict-like message with "tool_calls"
                tool_result_parts = ToolManager.execute_tool_requests(
                    self.clients, message_dict
                )

                # Add tool results back into the conversation as user/tool messages
                # Prefer service helper to keep parity with Claude flow
                self.gpt_service.add_user_message(self.messages, tool_result_parts)
                # Loop continues — next iteration will send the tool results back to the model
            else:
                final_text_response = message_content
                break

        return final_text_response
