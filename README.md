# Repo to Scroll (`repo2scroll`)

A command-line tool and Python library that transforms an entire project repository into a single, scroll-like text file. It intelligently filters files based on `.gitignore` rules, custom patterns, and file extensions, making it perfect for creating context files for LLMs, project snapshots, or code submissions.

## Features

- **Single Scroll Output**: Combines multiple source files into one continuous text file, like an ancient scroll.
- **Directory Tree**: Automatically includes a `tree`-like layout of the project structure at the top of the output file.
- **Smart Filtering**:
  - Respects `.gitignore` rules by default.
  - Option to disable `.gitignore` parsing (`--no-gitignore`).
  - Supports custom ignore files (e.g., `.dockerignore`) with the `--ignore-file` option.
  - Allows for on-the-fly exclusion patterns (`--exclude`).
- **Binary File Exclusion**: Automatically skips common binary files (images, archives, executables, etc.) to keep the output clean.
- **Cross-Platform**: Normalizes path separators to `/` for consistent output across Windows, macOS, and Linux.
- **Usable as a Library**: Import `bundle_project` into your Python scripts for programmatic use.
- **Rich CLI**: A user-friendly command-line interface with detailed help and examples.

## Your Request for Opinion on Ignore-File Handling

You asked for my opinion on moving away from a Git-only approach for ignoring files. Here's the philosophy I've implemented in this tool:

Many projects are managed with Git, so respecting `.gitignore` by default is a highly intuitive and useful feature that saves users from redefining common ignore patterns. It aligns with the principle of least surprise for most developers.

However, limiting the tool to only Git repositories is indeed restrictive. To provide flexibility, I've implemented the following tiered approach:

1.  **Keep `.gitignore` as the default:** The tool automatically uses `.gitignore` if it exists in the project root.
2.  **Add a `--no-gitignore` flag:** This allows users to completely disable the automatic reading of `.gitignore`.
3.  **Add an `--ignore-file` option:** This allows users to specify a custom ignore file (e.g., `.myignore`, `.dockerignore`). This can be used with or without `.gitignore`.
4.  **Keep `--exclude` for on-the-fly patterns:** For simple, one-off exclusions, this remains the most convenient method.

This approach offers a good balance between convention (sensible defaults) and configuration (flexibility for advanced use cases).

## Installation

You can install `repo2scroll` via pip. If you are installing from a local clone:

```bash
pip install .
```
Once published on PyPI, it will be:
```bash
pip install repo2scroll
```

## Usage

### As a Command-Line Tool

Once installed, you can use the `repo2scroll` command.

**Basic Usage**

```bash
# Turn the current directory into a scroll named 'combined_output.txt'
repo2scroll .

# Specify a project directory and an output file name
repo2scroll ./path/to/my-project -o project_snapshot.txt
```

**Excluding Files**

```bash
# Exclude all .log files and the 'dist/' directory
repo2scroll . --exclude "*.log" "dist/"

# Use a custom ignore file (like .dockerignore)
repo2scroll . --ignore-file .dockerignore

# Disable the default .gitignore behavior
repo2scroll . --no-gitignore
```

**Getting Help**

```bash
repo2scroll --help
```

### As a Python Library

You can also use `repo2scroll` within your own Python projects.

```python
from repo2scroll import bundle_project
from pathlib import Path

# Define project and output paths
project_directory = "./my-awesome-project"
output_file = "./bundle.txt"

# Ensure the project directory exists
if not Path(project_directory).is_dir():
    print(f"Error: Project directory '{project_directory}' not found.")
else:
    try:
        # Define extra patterns to ignore
        ignore_patterns = ["*.tmp", "credentials.json"]

        # Call the bundler function
        bundle_project(
            project_dir=project_directory,
            output_file=output_file,
            extra_ignore_patterns=ignore_patterns,
            use_gitignore=True  # This is the default
        )
        print(f"Project successfully bundled to '{output_file}'")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

```

## Output Format

The generated file has a simple and clean structure:

```text
<layout>
my-project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md
</layout>

<file path="src/main.py">
# Contents of src/main.py
...
</file>

<file path="src/utils.py">
# Contents of src/utils.py
...
</file>

...
```
