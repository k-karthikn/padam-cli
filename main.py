"""padam-cli entry point, including the installed console-script command."""

import asyncio
import sys

from rich.console import Console

from src.argparser import ArgParse
from src.config import Config
from src.media import Media
from src.scraper import ScrapeError
from src.search import Search


console = Console()


async def run(args: ArgParse, config: Config) -> int:
    search = Search(config)
    search.search_query = args.query
    search.search_year = args.year
    search.isdubsearch = args.isdubsearch
    search.list_latest = args.latest
    search.list_dubbed = args.dubbed
    if not await search.show_results_tui():
        return 1
    media = Media(search.selected_server_url, search.selected_movie["title"],
                  config.download_path, search.media_headers)
    return 0 if media.process(args.download) else 1


def main() -> int:
    try:
        args = ArgParse().parse()  # --help exits before any network request.
        config = Config()
        if not config.fetch_config():
            console.print("[yellow]Remote config unavailable; using saved domains.[/yellow]")
        return asyncio.run(run(args, config))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        return 130
    except (ScrapeError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
