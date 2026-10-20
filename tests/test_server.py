import asyncio
import os
import shutil
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_COMMAND = shutil.which(
    "media-downloader-mcp", path=str(Path(sys.executable).parent)
)


async def list_tools(download_directory: Path) -> dict:
    parameters = StdioServerParameters(
        command=SERVER_COMMAND,
        env={**os.environ, "MEDIA_DOWNLOAD_DIRECTORY": str(download_directory)},
    )

    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        listing = await session.list_tools()

    return {tool.name: tool.inputSchema["properties"].keys() for tool in listing.tools}


def test_server_exposes_download_tools(tmp_path: Path) -> None:
    assert SERVER_COMMAND, (
        "media-downloader-mcp is not installed in the test environment"
    )

    tools = asyncio.run(asyncio.wait_for(list_tools(tmp_path), timeout=120))

    assert {"download_media", "fetch_subtitles"} <= tools.keys()
    assert {"url", "format"} <= tools["download_media"]
    assert {"url", "language"} <= tools["fetch_subtitles"]
