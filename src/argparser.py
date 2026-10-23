import argparse


class ArgParse:
    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="padam-cli",
            description="Browse, stream and download Tamil movies."
        )

        # latest command
        parser.add_argument(
            "command",
            nargs="?",
            choices=["list-latest", "list-dubbed"],
            help="Show latest or dubbed movies"
        )

        # dubbed search flag
        parser.add_argument(
            "--dubbed",
            action="store_true",
            help="Search movie in dubbed lists"
        )

        # search
        parser.add_argument(
            "-s", "--search",
            nargs="+",
            metavar="MOVIE",
            help="Search movie"
        )

        # year
        parser.add_argument(
            "-y", "--year",
            type=str,
            metavar="YEAR",
            help="Movie year"
        )

        # play/download
        group = parser.add_mutually_exclusive_group()

        group.add_argument(
            "-p", "--play",
            action="store_true",
            help="Stream movie"
        )

        group.add_argument(
            "-d", "--download",
            action="store_true",
            help="Download movie (default)"
        )

        self.parser = parser

    def parse(self):
        args = self.parser.parse_args()
        if args.command and args.search:
            self.parser.error("Choose a command or --search, not both.")
        if args.year and not args.search:
            self.parser.error("--year requires --search.")
        if args.dubbed and not args.search:
            self.parser.error("--dubbed requires --search.")
        if not args.command and not args.search:
            self.parser.error("Enter --search MOVIE, list-latest, or list-dubbed.")

        self.query = " ".join(args.search) if args.search else None
        self.year = args.year
        self.isdubsearch = args.dubbed
        self.latest = args.command == "list-latest"
        self.dubbed = args.command == "list-dubbed"

        # Download is the default
        self.download = not args.play

        return self
