import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude
from core.gpt import GPT

from core.claude_cli_chat import CliChat
from core.gpt_cli_chat import CliChatGPT
from core.cli import CliApp

load_dotenv()

# Config
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

gpt_model = os.getenv("GPT_MODEL", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")

if not ((claude_model and anthropic_api_key) or (gpt_model and openai_api_key)):
    raise ValueError(
        "Error: Provide Claude credentials (CLAUDE_MODEL + ANTHROPIC_API_KEY) "
        "or GPT credentials (GPT_MODEL + OPENAI_API_KEY) in .env"
    )


async def main():
    use_model = os.getenv("AI_PROVIDER", "gpt").lower()

    if use_model == "claude":
        service = Claude(model=claude_model)
        ChatClass = CliChat
    elif use_model == "gpt":
        service = GPT(model=gpt_model)
        ChatClass = CliChatGPT
    else:
        raise ValueError(f"Invalid USE_MODEL value: {use_model}")

    server_scripts = sys.argv[1:]
    clients = {}

    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    async with AsyncExitStack() as stack:
        # Default document client
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        # Additional MCP servers from args
        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        # Pick Claude or GPT chat implementation
        chat = ChatClass(
            doc_client=doc_client,
            clients=clients,
            gpt_service=service if use_model == "gpt" else None,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
