[English](README.md) · [한국어](README.ko.md) · [中文](README.zh.md)

# media-downloader-mcp

A local MCP server that exposes [model-compose](https://github.com/hanyeol/model-compose) workflows as MCP tools, so MCP clients such as Claude can save videos, audio and subtitles from [any site yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), such as YouTube, Vimeo and SoundCloud, to your machine.

## Quick Start

You need [uv](https://docs.astral.sh/uv/), [Git](https://git-scm.com/) and [ffmpeg](https://ffmpeg.org/) on your `PATH`, a JS runtime such as [Deno](https://deno.com/) on your `PATH` for YouTube, and Google Chrome installed for sites that need you to sign in.

Register the server in your MCP client config.

```json
{
  "mcpServers": {
    "media-downloader-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.0", "media-downloader-mcp"],
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
claude mcp add media-downloader-mcp -- uvx --from git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.0 media-downloader-mcp
```

## Flow

```text
MCP client ──stdio──> model-compose (mcp-server controller)
                          │
                          ├─ download_media     → yt-dlp ──ok──> file-store (local)
                          │                          ├─sign-in needed──> open Chrome → interrupt → resume_workflow → collect cookies → yt-dlp → file-store (local)
                          │                          └─other error──> retry yt-dlp → file-store (local)
                          └─ fetch_subtitles    → yt-dlp ──ok──> subtitle text
                                                     ├─sign-in needed──> open Chrome → interrupt → resume_workflow → collect cookies → yt-dlp → subtitle text
                                                     └─other error──> retry yt-dlp → subtitle text
```

## Tools

| Tool | Input | Output |
| :---: | --- | --- |
| `download_media` | `url`, `format` (`mp4`, `webm` or `mkv` for video, `mp3`, `m4a`, `opus`, `flac` or `wav` for audio only, defaults to `mp4`) | `file_url` |
| `fetch_subtitles` | `url`, `language` (ISO 639-1, defaults to `en`) | `text` |
| `resume_workflow` | `task_id`, `job_id`, `run_id`, `answer` | Output of the resumed tool |

Files land in `MEDIA_DOWNLOAD_DIRECTORY` (defaults to `~/Downloads/media`) as `<run_id>.<extension>`, and the tools return only a `file://` URL instead of the file contents.

## Environment Variables

| Environment variable | Default | Description |
| :---: | :---: | --- |
| `MEDIA_DOWNLOAD_DIRECTORY` | `~/Downloads/media` | Where files are saved |
| `MEDIA_DOWNLOAD_BROWSER_PROFILE` | ✗ | Absolute path of a browser profile directory that keeps you signed in. When empty, the sign-in is lost when the server stops |
| `MEDIA_DOWNLOAD_BROWSER_CHANNEL` | `chrome` | Browser to open (`chrome`, `msedge` and so on) |

## Sites That Need Signing In

Each tool first tries without a browser, and if that fails with an error saying you need to sign in, it opens the URL in a Chrome window and stops with a `status: interrupted` response. Any other error gets one more try, and if that also fails, the error is returned. After you sign in there, the client calls `resume_workflow` with the response's `task_id` and `interrupt.job_id`, and the tool retries with only the cookies that browser holds for the requested URL and the page you end on after signing in.

## Notice

Many sites restrict downloads in their terms of service, and DRM-protected content cannot be downloaded. Check each site's terms and use this only for content you own or are allowed to download. This project is not affiliated with YouTube or any other supported site.
