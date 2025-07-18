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
- **Usable as a Library**: Import `bundle_project` to get the bundled content as a string for use in your Python scripts.
- **Rich CLI**: A user-friendly command-line interface with detailed help and examples.

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

Once installed, you can use the `repo2scroll` command to generate a file directly.

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
```

**Getting Help**

```bash
repo2scroll --help
```

### As a Python Library

You can also use `repo2scroll` within your own Python projects to get the bundled content as a string.

```python
from repo2scroll import bundle_project
from pathlib import Path

project_directory = "./my-awesome-project"

if not Path(project_directory).is_dir():
    print(f"Error: Project directory '{project_directory}' not found.")
else:
    try:
        # Define extra patterns to ignore
        ignore_patterns = ["*.tmp", "credentials.json"]

        # Call the bundler function to get the content as a string
        scroll_content = bundle_project(
            project_dir=project_directory,
            extra_ignore_patterns=ignore_patterns,
            use_gitignore=True  # This is the default
        )

        # Now you can use the string as needed
        print("--- Generated Scroll Content (first 500 chars) ---")
        print(scroll_content[:500] + "...")
        print("-------------------------------------------------")

        # Or write it to a file yourself
        with open("my_bundle.txt", "w", encoding="utf-8") as f:
            f.write(scroll_content)
        print("Content also saved to 'my_bundle.txt'")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
```

## Output Format

The generated content (string or file) has a simple and clean structure:

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
