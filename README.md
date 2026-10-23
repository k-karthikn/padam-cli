# padam-cli

A terminal app for finding Tamil and Tamil dubbed movie releases on supported public sources. It lets you choose a release, quality and server, then open the media URL in a browser, download it with `yt-dlp` or `ffmpeg`, or play it with `mpv`.

## Install

Python 3.10 or newer is required. From a checkout:

```bash
git clone https://github.com/k-karthikn/padam-cli.git
cd padam-cli
python -m pip install .
padam-cli --help
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run padam-cli --help
```

On Termux, install Python and the native libraries needed to build `lxml` before running `python -m pip install .`:

```bash
pkg install python clang libxml2 libxslt
```

`mpv`, `ffmpeg` and `yt-dlp` are optional external programs. Install the ones you intend to use. Browser handoff is available without them, though some servers require the source's referer or cookies and may not work in a separate browser.

To build a standalone executable on Linux or Windows, run `uv sync` followed by:

```bash
uv run pyinstaller --clean --onefile --name padam-cli main.py
```

The executable is written to `dist/`. `install.sh` and `install.ps1` build and install it on their respective platforms.

## Use

```bash
padam-cli -s leo -y 2023
padam-cli -s "Spider Man" --dubbed
padam-cli -s vikram --play
padam-cli list-latest
padam-cli list-dubbed
```

Searches are case-insensitive. A four-digit year narrows the catalogue; it is required for titles that start with a number or Tamil letter. Download is the default action, and `--play` launches `mpv`. The app displays the available movie, quality, episode and server choices interactively, including episodes on later pages of a season. `padam-cli --help` lists all options without accessing the network.

## Source configuration

At startup, the CLI fetches the `domains` from [this repository's config](https://github.com/k-karthikn/padam-cli/blob/master/config/config.json). The request has an eight-second timeout. A valid response is saved as the last known good domain pair under `~/.cache/padam-cli/config.json` (or `%LOCALAPPDATA%\padam-cli\config.json` on Windows). If the request fails, the saved domains are used; if there is no cache, the local config or built-in defaults are used. The remote file can change the two source domains without a CLI release. Other settings, including download path, remain local. The CLI deliberately uses its built-in repository URL as the update source, so a remote file cannot redirect future configuration requests.

When running from a source checkout, edit `config/config.json` for `download_path`, `headers`, `junk_titles`, or endpoint paths. A standalone executable reads local settings from `~/.config/padam-cli/config.json` (or `%APPDATA%\padam-cli\config.json` on Windows) if that file exists. The file may contain the same fields as the repository config. An invalid domain update never replaces the last known good domains.

The source websites may change their HTML or links independently of their domains. A domain update cannot repair those changes; the scraper may then need a code update. Search checks paginated catalogue pages and reports source errors rather than showing an empty result for a failed first page. Complete catalogue and episode lists are cached for 15 minutes under the same cache directory. Partial results from failed pages are never cached.

## Verify changes

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py src
```

## Disclaimer

This project does not host media. Use it only for content you are allowed to access and download, and follow the terms of the source websites. Availability depends on those third-party sites.

Licensed under the [MIT License](LICENSE).
