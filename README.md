[English](README.md) · [한국어](README.ko.md) · [中文](README.zh.md)

# media-downloader-mcp

A local MCP server that exposes [model-compose](https://github.com/hanyeol/model-compose) workflows as MCP tools, so MCP clients such as Claude can save videos, audio and subtitles from [any site yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), such as YouTube, Vimeo and SoundCloud, to your machine.

## Quick Start

| Tool | Needed for | Where |
| :---: | :---: | --- |
| [uv](https://docs.astral.sh/uv/) | Always | `PATH`, then run `uv tool update-shell` to add its tool directory to `PATH` |
| [Git](https://git-scm.com/) | Always | `PATH` |
| [ffmpeg](https://ffmpeg.org/) | Always | `PATH` |
| A JS runtime such as [Deno](https://deno.com/) | YouTube | `PATH` |
| Google Chrome | Sites that need you to sign in | Installed |

Install the server and run it once with empty input so it also installs its runtime packages.

> Installing the runtime packages first keeps the first connection from timing out.

```bash
# macOS and Linux
uv tool install git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.4
media-downloader-mcp < /dev/null
```

```powershell
# Windows
uv tool install git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.4
cmd /c "media-downloader-mcp < NUL"
```

Register the installed command in your MCP client config.

```json
{
  "mcpServers": {
    "media-downloader-mcp": {
      "command": "media-downloader-mcp",
      "env": {
        "MEDIA_DOWNLOAD_DIRECTORY": "~/Downloads/media",
        "MEDIA_DOWNLOAD_BROWSER_PROFILE": "/absolute/path/to/browser-profile"
      }
    }
  }
}
```

In Claude Code, one command registers it.

```bash
claude mcp add media-downloader-mcp -- media-downloader-mcp
```

## Flow

```text
MCP client ──stdio──> model-compose (mcp-server controller)
                          │
                          ├─ download_media     → yt-dlp ──ok──> file-store (local)
                          │                          ├─sign-in needed──> open Chrome → repeat (collect cookies → yt-dlp) up to 30 times → file-store (local)
                          │                          └─other error──> retry yt-dlp → file-store (local)
                          └─ fetch_subtitles    → yt-dlp ──ok──> subtitle text
                                                     ├─sign-in needed──> open Chrome → repeat (collect cookies → yt-dlp) up to 30 times → subtitle text
                                                     └─other error──> retry yt-dlp → subtitle text
```

## Tools

| Tool | Input | Output |
| :---: | --- | --- |
| `download_media` | `url`, `format` (`mp4`, `webm` or `mkv` for video, `mp3`, `m4a`, `opus`, `flac` or `wav` for audio only, defaults to `mp4`) | `file_url` |
| `fetch_subtitles` | `url`, `language` (ISO 639-1, defaults to `en`) | `text` |

Files land in `MEDIA_DOWNLOAD_DIRECTORY` (defaults to `~/Downloads/media`) as `<run_id>.<extension>`, and the tools return only a `file://` URL instead of the file contents.

## Environment Variables

| Environment variable | Default | Description |
| :---: | :---: | --- |
| `MEDIA_DOWNLOAD_DIRECTORY` | `~/Downloads/media` | Where files are saved |
| `MEDIA_DOWNLOAD_BROWSER_PROFILE` | ✗ | Absolute path of a browser profile directory that keeps you signed in. When empty, the sign-in is lost when the server stops |
| `MEDIA_DOWNLOAD_BROWSER_CHANNEL` | `chrome` | Browser to open (`chrome`, `msedge` and so on) |

## Sites That Need Signing In

Each tool first tries without a browser, and if that fails with an error saying you need to sign in, it opens the URL in a Chrome window. Once the window is open, the tool retries every 10 seconds, up to 30 times, with only the cookies that browser holds for the requested URL and the page it is on, so signing in there during that time lets the download go through. The tool call gets no response until then and each try adds its own download time, so set the MCP client's request timeout to 10 minutes or more.

## Notice

Many sites restrict downloads in their terms of service, and DRM-protected content cannot be downloaded. Check each site's terms and use this only for content you own or are allowed to download. This project is not affiliated with YouTube or any other supported site.
