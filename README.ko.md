[English](README.md) · [한국어](README.ko.md) · [中文](README.zh.md)

# media-downloader-mcp

[model-compose](https://github.com/hanyeol/model-compose) 워크플로(Workflow)를 MCP 도구로 노출해 Claude 같은 MCP 클라이언트(Client)가 [yt-dlp가 지원하는 사이트](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)(YouTube, Vimeo, SoundCloud 등)의 영상, 음성, 자막을 사용자 PC에 받게 하는 로컬(Local) MCP 서버(Server)다.

## 빠른 시작

| 도구 | 필요한 경우 | 위치 |
| :---: | :---: | --- |
| [uv](https://docs.astral.sh/uv/) | 항상 | `PATH`, `uv tool update-shell`로 도구 디렉터리(Directory)도 `PATH`에 추가 |
| [Git](https://git-scm.com/) | 항상 | `PATH` |
| [ffmpeg](https://ffmpeg.org/) | 항상 | `PATH` |
| [Deno](https://deno.com/) 같은 JS 런타임(Runtime) | YouTube | `PATH` |
| Google Chrome | 로그인이 필요한 사이트 | 설치만 |

서버를 설치하고 빈 입력으로 한 번 실행해 런타임 패키지(Package)까지 미리 설치한다.

> 런타임 패키지를 미리 설치해야 첫 연결이 타임아웃(Timeout)에 걸리지 않는다.

```bash
# macOS·Linux
uv tool install git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.3
media-downloader-mcp < /dev/null
```

```powershell
# Windows
uv tool install git+https://github.com/MindrLabs/media-downloader-mcp@v0.3.3
cmd /c "media-downloader-mcp < NUL"
```

MCP 클라이언트 설정에 설치한 명령을 등록한다.

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

Claude Code에서는 명령 한 줄로 등록한다.

```bash
claude mcp add media-downloader-mcp -- media-downloader-mcp
```

## 흐름

```text
MCP 클라이언트 ──stdio──> model-compose (mcp-server 컨트롤러)
                              │
                              ├─ download_media     → yt-dlp ──성공──> file-store (local)
                              │                          ├─로그인 필요──> Chrome 열기 → (쿠키 수집 → yt-dlp)를 최대 30번 반복 → file-store (local)
                              │                          └─기타 에러──> yt-dlp 재시도 → file-store (local)
                              └─ fetch_subtitles    → yt-dlp ──성공──> 자막 텍스트
                                                         ├─로그인 필요──> Chrome 열기 → (쿠키 수집 → yt-dlp)를 최대 30번 반복 → 자막 텍스트
                                                         └─기타 에러──> yt-dlp 재시도 → 자막 텍스트
```

## 도구

| 도구 | 입력 | 출력 |
| :---: | --- | --- |
| `download_media` | `url`, `format`(영상 `mp4`·`webm`·`mkv`, 음성만 `mp3`·`m4a`·`opus`·`flac`·`wav`, 기본 `mp4`) | `file_url` |
| `fetch_subtitles` | `url`, `language`(ISO 639-1, 기본 `en`) | `text` |

파일은 `MEDIA_DOWNLOAD_DIRECTORY`(기본 `~/Downloads/media`)에 `<run_id>.<확장자>` 이름으로 저장되고, 도구는 파일 내용 대신 `file://` URL만 돌려준다.

## 환경 변수

| 환경 변수 | 기본값 | 내용 |
| :---: | :---: | --- |
| `MEDIA_DOWNLOAD_DIRECTORY` | `~/Downloads/media` | 파일 저장 위치 |
| `MEDIA_DOWNLOAD_BROWSER_PROFILE` | ✗ | 로그인 상태를 저장할 브라우저(Browser) 프로필(Profile) 디렉터리의 절대 경로. 비우면 서버가 꺼질 때 로그인 상태도 사라진다 |
| `MEDIA_DOWNLOAD_BROWSER_CHANNEL` | `chrome` | 띄울 브라우저(`chrome`, `msedge` 등) |

## 로그인이 필요한 사이트

도구는 먼저 브라우저 없이 받아 보고, 로그인이 필요하다는 에러(Error)로 실패하면 Chrome 창에 그 URL을 연다. 창을 연 뒤에는 요청한 URL과 지금 머문 페이지의 쿠키(Cookie)만 그 브라우저에서 모아 다시 받는 것을 10초 간격으로 최대 30번 반복하므로 그 사이에 그 창에서 로그인하면 이어서 받는다. 그동안 도구 호출은 응답 없이 이어지고 시도마다 받는 시간도 더해지므로 MCP 클라이언트의 요청 타임아웃은 10분 이상으로 잡는다.

## 주의

많은 사이트가 서비스 약관으로 콘텐츠 다운로드를 제한하고, DRM이 걸린 콘텐츠는 받을 수 없다. 사이트 약관을 확인하고 본인이 권리를 가졌거나 다운로드가 허용된 콘텐츠에만 쓴다. 이 프로젝트는 YouTube를 비롯해 지원하는 어떤 사이트와도 제휴 관계가 없다.
