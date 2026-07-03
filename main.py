from src.argparser import ArgParse
from src.search import Search
from src.media import Media
from rich.console import Console
from src.config import Config
import asyncio
import sys

console = Console()
async def main():
    config = Config()
    args = ArgParse()
    search = Search()
    
    config.fetch_config()
    args.parse()

    if args.query:
        search.search_query = args.query
        search.search_year = args.year
        search.isdubsearch = args.isdubsearch

        await search.show_results_tui()
        media = Media(url=search.selected_server_url, title=search.selected_movie["title"])
        media.process(args.download)
    elif args.latest:
        search.list_latest = args.latest
        await search.show_results_tui()
        media = Media(url=search.selected_server_url, title=search.selected_movie["title"])
        media.process(args.download)
    elif args.dubbed:
        search.list_dubbed = args.dubbed
        await search.show_results_tui()
        media = Media(url=search.selected_server_url, title=search.selected_movie["title"])
        media.process(args.download)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[bold red]\n[!] Process interrupted by user. Exiting.............[/bold red]")
        sys.exit(0)
