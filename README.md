## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Disclaimer](#disclaimer)
- [Installation](#installation)
  - [Prebuilt Binaries](#prebuilt-binaries)
  - [Building from Source](#building-from-source)
- [Download Methods](#download-methods)
- [Media Playback](#media-playback)
- [Usage](#usage)
- [Examples](#examples)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

# padam-cli

`padam-cli` is an open-source command-line application for browsing, streaming, and downloading Tamil movies from supported public sources.

It provides an interactive terminal interface for searching movies, viewing available releases, selecting video quality, and opening media links for streaming or downloading. Downloads can be performed using a web browser, `ffmpeg`, or `yt-dlp`, depending on your preferred workflow.

The project is designed for users who prefer a terminal-based experience without relying on a graphical interface. It runs on Linux, Windows, and Android through Termux.

## Quick Start

```bash
# Download the latest release
chmod +x padam-cli
./padam-cli list-latest

# Search for dubbed movies
./padam-cli -s Spider Man --dubbed

# Search for a movies
padam-cli -s vikram

# Stream
padam-cli -s vikram -p
```

## Features

* Search Tamil movies by title.
* Filter search results by release year.
* Browse the latest available movie releases.
* Search and browse Tamil dubbed movies.
* View available video qualities before playback or download.
* Stream movies directly from the terminal using `mpv`.
* Download media using your preferred method:

  * Web browser
  * `ffmpeg`
  * `yt-dlp`
* Interactive terminal interface for selecting movies and download options.
* Cross-platform support for Linux, Windows, and Termux.
* Configurable download location.
* Lightweight with minimal runtime dependencies.

## Disclaimer

`padam-cli` is an open-source command-line tool that retrieves publicly available movie metadata and media links from third-party websites.

The project does not host, store, upload, redistribute, or stream any copyrighted content. All media, trademarks, and other intellectual property remain the property of their respective owners.

Users are responsible for ensuring that their use of this software complies with applicable laws, regulations, and the terms of service of the websites they access.

This software is provided for educational and research purposes, without warranty of any kind. The author is not responsible for any misuse of the project or for any consequences resulting from its use.

## Installation

### Prebuilt binaries

Precompiled binaries are available on the project's GitHub Releases page. They can be used without installing Python or any project dependencies.

#### Linux

Download the binary that matches your system architecture, then make it executable:

```bash
chmod +x padam-cli
```

Install it system-wide:

```bash
sudo mv padam-cli /usr/local/bin/
```

Or install it for the current user:

```bash
mkdir -p ~/.local/bin
mv padam-cli ~/.local/bin/
```

If you installed it to `~/.local/bin`, ensure that directory is included in your `PATH`.

Verify the installation:

```bash
padam-cli --help
```

#### Windows

Download `padam-cli.exe` from the latest release and place it in any directory.

To run it from any terminal, add that directory to your `PATH` environment variable.

Verify the installation:

```powershell
padam-cli --help
```

#### Termux

Download the ARM64 binary from the latest release.

Make it executable:

```bash
chmod +x padam-cli
```

Move it into Termux's binary directory:

```bash
mv padam-cli $PREFIX/bin/
```

Verify the installation:

```bash
padam-cli --help
```

### Optional dependencies

The prebuilt binary is fully functional on its own. The following programs enable additional features:

| Dependency | Purpose                                 | Required |
| ---------- | --------------------------------------- | :------: |
| `mpv`      | Stream media directly from the terminal |    No    |
| `ffmpeg`   | Download media using FFmpeg             |    No    |
| `yt-dlp`   | Download media using yt-dlp             |    No    |

If these tools are not installed, you can still copy the generated media URL and open it manually in a web browser or your preferred media player.

## Building from source

Building from source requires Python 3.14 or later.

### Linux

Install the optional runtime tools if you plan to stream or download media:

**Arch Linux**

```bash
sudo pacman -S ffmpeg yt-dlp mpv
```

**Ubuntu / Debian**

```bash
sudo apt install ffmpeg yt-dlp mpv
```

**Fedora**

```bash
sudo dnf install ffmpeg yt-dlp mpv
```

Clone the repository:

```bash
git clone https://github.com/e-Zephyr/padam-cli.git
cd padam-cli
```

#### Using uv (Recommended)

```bash
uv sync
```

#### Using pip

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Build the executable:

```bash
pyinstaller --clean --onefile --name padam-cli main.py
```

The compiled binary will be available in the `dist/` directory.

### Windows

Clone the repository:

```bash
git clone https://github.com/e-Zephyr/padam-cli.git
cd padam-cli
```

#### Using uv (Recommended)

```bash
uv sync
uv run pyinstaller --clean --onefile --name padam-cli main.py
```

#### Using pip

```bash
pip install requirements.txt
```

Build the executable:

```bash
pyinstaller --clean --onefile --name padam-cli main.py
```

The executable will be generated in the `dist/` directory.

### Termux

> `uv` is currently not supported due to Python version compatibility. Install the dependencies manually.

Install the required packages:

```bash
pkg install clang libxml2 libxslt
```

Install the Python dependencies:

```bash
pip install requirements.txt
```

Build the executable:

```bash
pyinstaller --clean --onefile --name padam-cli main.py
```

Install it:

```bash
mv dist/padam-cli $PREFIX/bin/
```

Verify the installation:

```bash
padam-cli --help
```

## Download methods

`padam-cli` supports multiple download methods, allowing you to choose the one that best fits your workflow.

| Method      | Description                                             | Best suited for                                             |
| ----------- | ------------------------------------------------------- | ----------------------------------------------------------- |
| Web Browser | Opens the direct media URL in your default web browser. | Users who prefer their browser's built-in download manager. |
| `ffmpeg`    | Downloads media directly using FFmpeg.                  | Large downloads and HLS (`.m3u8`) streams.                  |
| `yt-dlp`    | Downloads media using yt-dlp.                           | Sources supported by yt-dlp and advanced download options.  |

The available download methods depend on the software installed on your system. If `ffmpeg` or `yt-dlp` is not available, `padam-cli` will continue to work using the remaining supported methods.

Download performance depends on the media source, server response, network conditions, and the selected download method. No single method is consistently faster in every situation, so you can choose the one that works best for your use case.

## Media playback

`padam-cli` supports direct media playback through `mpv`. When the **Play** option is selected, the generated media URL is passed to `mpv`, allowing playback without downloading the file first.

If `mpv` is not installed, you can still copy the generated media URL and open it manually in any media player or web browser that supports the media format.

`mpv` is the recommended player because of its native support for network streams and wide range of supported audio and video formats.

## Usage

```
padam-cli [OPTIONS] [COMMAND]
```

### Commands

| Command       | Description                                  |
| ------------- | -------------------------------------------- |
| `list-latest` | Display the latest available movie releases. |
| `list-dubbed` | Display a list of available dubbed movies.   |

### Options

| Option                   | Description                                     |
| ------------------------ | ----------------------------------------------- |
| `-s`, `--search <movie>` | Search for a movie by title.                    |
| `-y`, `--year <year>`    | Filter search results by release year.          |
| `--dubbed`               | Search only dubbed movies.                      |
| `-p`, `--play`           | Stream the selected movie using `mpv`.          |
| `-d`, `--download`       | Download the selected movie (default behavior). |
| `-h`, `--help`           | Display the help message and exit.              |

### Notes

* Searches are case-insensitive.
* If neither `--play` nor `--download` is specified, the selected movie is downloaded by default.
* Some titles that begin with numbers (for example, `24` or `96`) may require the release year to identify the correct movie.

## Examples

Search for a movie by title:

```bash id="ejj4xu"
padam-cli -s karuppu
```

Search for a movie released in a specific year:

```bash id="rmv9d5"
padam-cli -s karuppu -y 2026
```

Stream a movie without downloading it:

```bash id="uvh5zr"
padam-cli -s karuppu -y 2026 --play
```

Download a movie (default behavior):

```bash id="abf38n"
padam-cli -s karuppu -y 2026
```

List the latest available movie releases:

```bash id="u0rgoa"
padam-cli list-latest
```

Search only dubbed movies:

```bash id="a4qehn"
padam-cli -s "Spider-Man" --dubbed
```

Browse available dubbed movies:

```bash id="v53qpd"
padam-cli list-dubbed
```

Search for movies with numeric titles by specifying the release year:

```bash id="1ovjlwm"
padam-cli -s 24 -y 2016
```

```bash id="4wx6dq"
padam-cli -s 96 -y 2018
```

## Limitations

* `padam-cli` relies on publicly accessible third-party websites. Changes to those websites may temporarily affect functionality until the project is updated.
* An active internet connection is required to search, stream, or download media.
* The availability of movies, video qualities, and download methods depends on the source website.
* Streaming requires `mpv` to be installed and available in your system `PATH`.
* Some download methods require additional software, such as `ffmpeg` or `yt-dlp`.
* The project currently focuses on Tamil movies and supported Tamil dubbed content.

## Contributing

Contributions are welcome. Whether it's reporting bugs, improving documentation, fixing issues, or adding new features, every contribution helps improve the project.

If you encounter a bug or have a feature request, please open an issue before submitting a pull request for significant changes. This helps avoid duplicate work and provides an opportunity to discuss the proposed solution.

Before submitting a pull request, ensure that your changes are well-tested and follow the existing project structure and coding style.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE)