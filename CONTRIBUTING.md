# Contributing to padam-cli

Thank you for your interest in contributing to **padam-cli**! We welcome bug reports, documentation updates, feature requests, and code contributions from everyone.

This guide outlines our development workflow and standards to help you get started quickly.

---

## Prerequisites & Local Setup

### Prerequisites

- **Python**: Version `3.10` or higher.
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or standard Python `pip` and `venv`.
- **Git**: Installed and configured.
- **Optional Tools**:
  - `mpv`: For streaming playback (`--play`).
  - `ffmpeg` / `yt-dlp`: For media downloads.
  - *Termux/Linux build requirements* (if compiling `lxml` from source): `clang`, `libxml2`, `libxslt`.

### Step-by-Step Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/padam-cli.git
   cd padam-cli
   ```

2. **Set up the development environment:**

   - **Option A: Using `uv` (Recommended)**
     ```bash
     # Install all dependencies and create virtual environment
     uv sync
     ```

   - **Option B: Using standard `venv` and `pip`**
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # On Windows: .venv\Scripts\activate
     python -m pip install --upgrade pip
     python -m pip install -e .
     ```

3. **Verify local setup and run the CLI:**

   - With `uv`:
     ```bash
     uv run padam-cli --help
     ```
   - With activated virtual environment:
     ```bash
     python main.py --help
     # or
     padam-cli --help
     ```

---

## Development Workflow

### Branching Strategy

- The default development branch is **`master`**.
- Always branch off the latest `master` when starting work:
  ```bash
  git checkout master
  git pull origin master
  git checkout -b <branch-type>/<short-description>
  ```
- Use descriptive branch naming prefixes:
  - `feat/` for new features (e.g., `feat/add-json-output`)
  - `fix/` for bug fixes (e.g., `fix/scraper-pagination`)
  - `docs/` for documentation changes (e.g., `docs/update-readme`)
  - `refactor/` for code restructuring without behavioral change

### Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) to keep the commit history readable and consistent:

```text
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

Common types:
- `feat`: A new feature or capability
- `fix`: A bug fix
- `docs`: Documentation only changes
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Maintenance tasks, dependency updates, build changes

**Examples:**
- `feat(scraper): support next-page pagination on episode catalogue`
- `fix(config): prevent invalid remote update from overriding cache`
- `docs: update installation instructions for Termux`

---

## Code Quality & Testing

Before committing changes or opening a pull request, ensure all tests and bytecode validations pass.

### 1. Run the Test Suite

Run unit tests using Python's built-in `unittest` runner:

- **Using `uv`:**
  ```bash
  uv run python -m unittest discover -s tests -v
  ```

- **Using activated virtual environment:**
  ```bash
  python -m unittest discover -s tests -v
  ```

### 2. Syntax & Bytecode Compilation Check

Validate Python syntax across all source and entry files:

- **Using `uv`:**
  ```bash
  uv run python -m compileall -q main.py src
  ```

- **Using standard Python:**
  ```bash
  python -m compileall -q main.py src
  ```

### 3. Writing Tests

- Place new test files in the `tests/` directory prefixed with `test_` (e.g., `tests/test_new_feature.py`).
- Write self-contained tests using `unittest` or mock responses using `httpx` handlers rather than making live external network requests.

---

## Pull Request Process

When you are ready to submit your contribution:

1. **Keep changes focused**: One logical change per pull request. Avoid mixing unrelated refactors or formatting changes with feature code.
2. **Sync with upstream**:
   ```bash
   git fetch origin
   git rebase origin/master
   ```
3. **Verify checks locally**:
   - Ensure `python -m unittest discover -s tests -v` passes.
   - Ensure `python -m compileall -q main.py src` reports no errors.
4. **Push your branch**:
   ```bash
   git push origin <your-branch-name>
   ```
5. **Open a Pull Request**:
   - Title your PR concisely following conventional commit style.
   - Describe what changed and why.
   - Reference any relevant issues (e.g., `Closes #12` or `Fixes #34`).

### PR Checklist

- [ ] Branch is rebased onto the latest `master`.
- [ ] Code compiles without syntax errors (`python -m compileall -q main.py src`).
- [ ] All unit tests pass (`python -m unittest discover -s tests -v`).
- [ ] New tests have been added for any new features or bug fixes.
- [ ] Relevant documentation (e.g., `README.md`) has been updated if flags or behaviors changed.

---

## Reporting Issues

If you find a bug or have an idea for a feature, please let us know through GitHub Issues!

### Reporting Bugs

Before submitting an issue, search the [existing issues](https://github.com/k-karthikn/padam-cli/issues) to avoid duplicates.

When opening a bug report, please include:
- **CLI & Python version**: Run `python --version` and note the CLI release version.
- **OS & Environment**: e.g., Ubuntu 24.04, Arch Linux, macOS, Termux, Windows.
- **Command executed**: The exact CLI arguments and flags used.
- **Expected vs. actual behavior**: What you expected to happen vs. what occurred.
- **Traceback / Logs**: Complete error output or terminal logs (mask any sensitive information).

### Requesting Features

Feature requests are welcome! Please open an issue with:
- A clear description of the problem or opportunity.
- The proposed solution or behavior, including example command-line syntax if applicable.
- Any alternative solutions or workarounds you've considered.

---

Thank you for helping make **padam-cli** better!
