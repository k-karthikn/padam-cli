## Disclaimer

padam-cli is an open-source command-line tool that automates browsing and retrieving publicly accessible metadata and links from third-party websites.

This project does not host, store, distribute, stream, or upload any copyrighted media. All content, trademarks, and copyrights belong to their respective owners.

Users are solely responsible for ensuring that their use of this software complies with applicable laws, regulations, and the terms of service of any websites they access.

The author of this project is not responsible for how the software is used and does not encourage copyright infringement or unauthorized distribution of copyrighted material.

This project is provided for educational and research purposes only, without warranty of any kind.

padam-cli is a terminal-based browser for movie metadata and publicly available links.

Features:

* Browse movie listings from supported sources
* View movie metadata
* Select available quality options
* Open or process available media links

padam-cli does not host or redistribute media files.
# Installation (Precompiled Binary)
If you don't want to install Python or any dependencies, you can use the precompiled binary available from the latest release.
## Linux
1. Download the latest Linux binary from the **Releases** page.
2. Make the binary executable:
```bash
chmod +x padam-cli
```
3. Move it to a directory in your `PATH`:
**System-wide installation**
```bash
sudo mv padam-cli /usr/local/bin/
```
**User-only installation**
```bash
mkdir -p ~/.local/bin
mv padam-cli ~/.local/bin/
```
> Make sure `~/.local/bin` is included in your `PATH`.
4. Verify the installation:
```bash
padam-cli --help
```
---
## Windows
1. Download the latest `padam-cli.exe` from the **Releases** page.
2. Move the executable to any folder.
3. Add that folder to your **Path** environment variable.
4. Open a new Command Prompt or PowerShell window.
5. Verify the installation:
```powershell
padam-cli --help
```
---
## Termux (Android)
1. Download the latest ARM64 binary from the **Releases** page.
2. Make it executable:
```bash
chmod +x padam-cli
```
3. Move it to Termux's binary directory:
```bash
mv padam-cli $PREFIX/bin/
```
4. Verify the installation:
```bash
padam-cli --help
```
---
## Notes
* Download the binary that matches your operating system and CPU architecture.
* The precompiled binary does **not** require Python or project dependencies.
* Some features require external tools:
  * **yt-dlp** *(optional)* — Download videos using `yt-dlp`.
  * **FFmpeg** *(optional)* — Download and process media using FFmpeg.
  * **mpv** *(optional)* — Required only if you want to stream videos directly from the terminal.
* If you don't install **mpv**, you can simply copy the generated video URL and play it using any media player or web browser of your choice.
If you'd like, I can also make it look more like professional GitHub projects with tabs, callout blocks, and platform badges.

# Installation(Linux)
Installing **padam-cli** on Linux is simple.
## 1. Install Optional Downloaders
`padam-cli` works out of the box using your default web browser for downloads. However, installing `ffmpeg` and `yt-dlp` gives you more download options.
### Arch Linux
```bash
sudo pacman -S yt-dlp ffmpeg
```
### Ubuntu / Debian
```bash
sudo apt install yt-dlp ffmpeg
```
### Fedora
```bash
sudo dnf install yt-dlp ffmpeg
```
## Which Downloader Should You Use?
You can choose whichever fits your workflow.
* **yt-dlp**
  * ⚡ Very fast startup
  * 🐢 Usually slower download speed
* **ffmpeg**
  * 🐢 Slow startup (takes time to begin downloading)
  * ⚡ Usually the fastest download speed
* **Web Browser**
  * ⚡ Instant startup
  * 🚀 Standard download speed
In reality, download speeds vary depending on the server. Sometimes the web browser can even reach **10+ MB/s**, while `ffmpeg` may spend a few seconds preparing the download. That's why **padam-cli lets you choose whichever downloader you prefer**.
## 2. Install a Media Player
Streaming doesn't require downloading the movie first.
The recommended player is **mpv**.
If you prefer another player (such as VLC), you'll need to copy the generated stream URL and open it manually in your preferred media player.
### Arch Linux
```bash
sudo pacman -S mpv
```
### Ubuntu / Debian
```bash
sudo apt install mpv
```
### Fedora
```bash
sudo dnf install mpv
```
## 3. Clone the Repository
```bash
git clone https://github.com/e-Zephyr/padam-cli.git
cd padam-cli
```
Or download the project as a ZIP file and extract it.
## 4. Run the Installer
```bash
chmod +x install.sh
./install.sh
```
## 5. Add padam-cli to Your PATH
For Fish shell:
```bash
fish_add_path ~/.local/share/bin
```
For Bash or Zsh:
```bash
export PATH="$HOME/.local/share/bin:$PATH"
```
(Add the above line to your shell configuration file if needed.)
## 6. Verify the Installation
```bash
padam-cli -h
```
If the help menu appears, you're ready to use **padam-cli**.


# Installation (Windows)
There are two ways to build **padam-cli** on Windows.
## Option 1: Using uv (Recommended)
If you already have `uv` installed, simply clone the repository and run:
```bash
uv sync
uv run pyinstaller --clean --onefile --name padam-cli main.py
```
The compiled executable will be available in the `dist` folder.
---
## Option 2: Using Python + pip
If you don't use `uv`, first install the required dependencies:
```bash
pip install beautifulsoup4 httpx InquirerPy lxml rich pyinstaller
```
Or install them individually:
```text
beautifulsoup4>=4.15.0
httpx>=0.28.1
InquirerPy>=0.3.4
lxml>=6.1.1
rich>=15.0.0
```
Then build the executable:
```bash
pyinstaller --clean --onefile --name padam-cli main.py
```
After the build finishes, you'll find the executable inside the `dist` folder.

# Installation (Termux)
> **Note:** `uv` is currently not supported on Termux for this project due to Python version compatibility. Install the dependencies manually.
## 1. Install Python dependencies
Install all required packages:
```bash
pip install beautifulsoup4 httpx InquirerPy lxml rich pyinstaller
```
Or install them individually:
```text
beautifulsoup4>=4.15.0
httpx>=0.28.1
InquirerPy>=0.3.4
lxml>=6.1.1
rich>=15.0.0
pyinstaller>=6.21.0
```
## 2. Resolve build errors (if any)
If you encounter errors while installing **lxml** or other packages, install the required system packages first:
```bash
pkg install ldd libxml2 libxslt clang
```
Then run the `pip install` command again.
## 3. Build the binary
Compile the project into a standalone executable:
```bash
pyinstaller --clean --onefile --name padam-cli main.py
```
The compiled binary will be available in the `dist/` directory.
## 4. Add the binary to your PATH
Move the binary to Termux's binary directory:
```bash
mv dist/padam-cli $PREFIX/bin/
```
Or, if you prefer, move it to any directory that is included in your `PATH`.
### Fish shell
If you're using Fish, you can add your own directory to the `PATH`:
```fish
fish_add_path ~/.local/bin
```
Then move the binary there:
```bash
mkdir -p ~/.local/bin
mv dist/padam-cli ~/.local/bin/
```
## 5. Verify the installation
```bash
padam-cli --help
```
# Usage
```
usage: padam-cli [-h] [--dubbed] [-s MOVIE] [-y YEAR] [-p | -d [{list-latest,list-dubbed}]
Browse, stream and download Tamil movies.

positional arguments: {list-latest,list-dubbed} Show latest or dubbed movies

options:
  -h, --help            show this help message and exit
  --dubbed              Search movie in dubbed lists
  -s, --search MOVIE    Search movie
  -y, --year YEAR       Movie year
  -p, --play            Stream movie
  -d, --download        Download movie (default)
```
## Search Examples
Search for all movies containing the word **karuppu**:
```bash
padam-cli -s karuppu
```
Search only the **2026** movies containing **karuppu**:
```bash
padam-cli -s karuppu -y 2026
```
Searches are **case-insensitive**, so the following are treated the same:
```bash
padam-cli -s karuppu
padam-cli -s Karuppu
padam-cli -s KARUPPU
```
## Download vs Stream
If you don't specify `-p` or `-d`, **padam-cli downloads the movie by default**.
To stream the movie instead of downloading it, pass the `-p` (or `--play`) option:
```bash
padam-cli -s karuppu -y 2026 -p
```
or
```bash
padam-cli --search karuppu --year 2026 --play
```
This will open the stream directly in **mpv** without downloading the movie.
## Movies That Start With Numbers
Some movie titles begin with numbers, such as **24** or **96**. In these cases, you should also specify the release year to avoid ambiguous results.
```bash
padam-cli -s 24 -y 2016
```
```bash
padam-cli -s 96 -y 2018
```
## Latest Movies
`padam-cli` can also show the latest movies added to the website.
```bash
padam-cli list-latest
```
This fetches the latest movies available, including newly added OTT releases and theater prints.

## Dubbed Movies

There are two methods to find dubbed movies. 

*   **Targeted Search (Recommended):** Append the `--dubbed` flag to your standard search query to find specific dubbed titles.
    ```bash
    padam-cli s <query> --dubbed
    ```
    > **Examples:** *Spider-Man (2004)*, *Pirates of the Caribbean 3 (2007)*

*   **Broad Listing:** View a general list of available dubbed movies. This command outputs a curated subset and is generally less useful than targeted searching.
    ```bash
    padam-cli list-dubbed
    ```
    > **Examples:** *Sunday (2008)*, *Plot Paramasivan (2026)*, *Phobia (2016)*, *2 Friends (2018)*

# Contribution
Contributions are always welcome—and honestly, they're needed to make **padam-cli** better.
Whether it's fixing bugs, adding new features, improving performance, or even correcting documentation, every contribution helps.
If you're interested, feel free to open an issue, submit a pull request, or share your ideas.
Thanks for checking out **padam-cli**. Hope you'll be part of the project
