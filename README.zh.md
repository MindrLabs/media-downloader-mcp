[English](README.md) · [한국어](README.ko.md) · [中文](README.zh.md)

# media-downloader-mcp

一个本地 MCP 服务器，把 [model-compose](https://github.com/hanyeol/model-compose) 工作流暴露为 MCP 工具，让 Claude 等 MCP 客户端把 [yt-dlp 支持的网站](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)（YouTube、Vimeo、SoundCloud 等）上的视频、音频和字幕保存到你的电脑上。

## 快速开始

`PATH` 中需要有 [uv](https://docs.astral.sh/uv/)、[Git](https://git-scm.com/) 和 [ffmpeg](https://ffmpeg.org/)，下载 YouTube 还需要 `PATH` 中有 [Deno](https://deno.com/) 等 JS 运行时，需要登录的网站还要求安装 Google Chrome。

在 MCP 客户端配置中注册服务器。

```json
{
  "mcpServers": {
    "media-downloader-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.1", "media-downloader-mcp"],
      "env": {
        "MEDIA_DOWNLOAD_DIRECTORY": "~/Downloads/media",
        "MEDIA_DOWNLOAD_BROWSER_PROFILE": "/absolute/path/to/browser-profile"
      }
    }
  }
}
```

在 Claude Code 中用一条命令即可注册。

```bash
claude mcp add media-downloader-mcp -- uvx --from git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.1 media-downloader-mcp
```

## 流程

```text
MCP 客户端 ──stdio──> model-compose (mcp-server 控制器)
                          │
                          ├─ download_media     → yt-dlp ──成功──> file-store (local)
                          │                          ├─需要登录──> 打开 Chrome → 暂停 → resume_workflow → 收集 Cookie → yt-dlp → file-store (local)
                          │                          └─其他错误──> 重试 yt-dlp → file-store (local)
                          └─ fetch_subtitles    → yt-dlp ──成功──> 字幕文本
                                                     ├─需要登录──> 打开 Chrome → 暂停 → resume_workflow → 收集 Cookie → yt-dlp → 字幕文本
                                                     └─其他错误──> 重试 yt-dlp → 字幕文本
```

## 工具

| 工具 | 输入 | 输出 |
| :---: | --- | --- |
| `download_media` | `url`、`format`（视频为 `mp4`、`webm` 或 `mkv`，仅音频为 `mp3`、`m4a`、`opus`、`flac` 或 `wav`，默认 `mp4`） | `file_url` |
| `fetch_subtitles` | `url`、`language`（ISO 639-1，默认 `en`） | `text` |
| `resume_workflow` | `task_id`、`answer` | 恢复的工具的输出 |

文件以 `<run_id>.<扩展名>` 的名字保存在 `MEDIA_DOWNLOAD_DIRECTORY`（默认 `~/Downloads/media`）中，工具只返回 `file://` URL，不返回文件内容。

## 环境变量

| 环境变量 | 默认值 | 说明 |
| :---: | :---: | --- |
| `MEDIA_DOWNLOAD_DIRECTORY` | `~/Downloads/media` | 文件保存位置 |
| `MEDIA_DOWNLOAD_BROWSER_PROFILE` | ✗ | 用于保持登录状态的浏览器配置目录的绝对路径。留空时服务器停止后登录状态也会丢失 |
| `MEDIA_DOWNLOAD_BROWSER_CHANNEL` | `chrome` | 要打开的浏览器（`chrome`、`msedge` 等） |

## 需要登录的网站

工具会先在不打开浏览器的情况下下载，如果因需要登录的错误而失败，就在 Chrome 窗口中打开该 URL，并返回 `status: interrupted` 响应后暂停。其他错误会再尝试一次，如果仍然失败就返回该错误。你在该窗口登录后，客户端用响应中的 `task_id` 和以响应中 `interrupt` 列表的 `id` 为键的 `answer`（如 `{"<id>": null}`）调用 `resume_workflow`，工具就会只收集该浏览器中属于所请求 URL 和登录后停留页面的 Cookie 并重新下载。

## 注意

许多网站在服务条款中限制下载内容，受 DRM 保护的内容也无法下载。请查看各网站的条款，只用于你拥有权利或被允许下载的内容。本项目与 YouTube 及其他任何受支持的网站均无关联。
