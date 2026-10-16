"""TabMaker: turns a song recording into guitar tab and chord sheets."""

__version__ = "0.1.0"


def main() -> None:
    from tabmaker.cli import main as cli_main

    cli_main()
