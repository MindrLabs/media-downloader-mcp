from importlib.resources import as_file, files

from mindor.cli.compose import compose_command


def main() -> None:
    with as_file(files(__name__) / "model-compose.yml") as compose_file:
        compose_command.main(
            ["-f", str(compose_file), "up"], prog_name="media-downloader-mcp"
        )
