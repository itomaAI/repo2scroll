# src/repo2scroll/main.py

import os
import argparse
import logging
from pathlib import Path
import pathspec
from typing import List, Dict, Set, Optional

# --- Constants ---

logger = logging.getLogger(__name__)

# Default patterns to always ignore. Git metadata is a common one.
DEFAULT_IGNORE_PATTERNS: List[str] = [
    ".git/",
]

# Set of file extensions to be treated as binary.
# All extensions should be lowercase.
BINARY_EXTENSIONS: Set[str] = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp', '.tif', '.tiff',
    # Archives
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # Executables & Libraries
    '.exe', '.dll', '.so', '.o', '.a', '.lib', '.jar', '.class', '.pyc',
    # Audio & Video
    '.mp3', '.wav', '.mp4', '.mov', '.avi', '.mkv',
    # Fonts
    '.woff', '.woff2', '.ttf', '.otf', '.eot',
    # Other
    '.db', '.sqlite3', '.lock', '.DS_Store',
}

# --- Private Helper Functions ---

def _get_ignore_spec(
    root_path: Path,
    use_gitignore: bool,
    custom_ignore_file: Optional[Path],
    extra_patterns: List[str]
) -> pathspec.PathSpec:
    """
    Builds a pathspec.PathSpec object from various ignore sources.
    """
    all_patterns = DEFAULT_IGNORE_PATTERNS[:]

    if use_gitignore:
        gitignore_file = root_path / ".gitignore"
        if gitignore_file.is_file():
            try:
                with open(gitignore_file, "r", encoding="utf-8") as f:
                    all_patterns.extend(f.readlines())
                logger.info("Loaded ignore patterns from '.gitignore'.")
            except Exception as e:
                logger.warning(f"Failed to read '.gitignore': {e}")

    if custom_ignore_file:
        if custom_ignore_file.is_file():
            try:
                with open(custom_ignore_file, "r", encoding="utf-8") as f:
                    all_patterns.extend(f.readlines())
                logger.info(f"Loaded ignore patterns from '{custom_ignore_file.name}'.")
            except Exception as e:
                logger.warning(f"Failed to read custom ignore file '{custom_ignore_file}': {e}")
        else:
            logger.warning(f"Custom ignore file not found: '{custom_ignore_file}'")


    if extra_patterns:
        all_patterns.extend(extra_patterns)
        logger.info(f"Applying extra ignore patterns: {extra_patterns}")

    cleaned_patterns = [p.strip() for p in all_patterns if p.strip()]
    return pathspec.PathSpec.from_lines("gitwildmatch", cleaned_patterns)


def _generate_tree_structure(paths: List[Path], root_name: str) -> str:
    """
    Generates a tree-like string representation of the directory structure.
    """
    if not paths:
        return f"{root_name}/\n(No files included)"

    tree_dict: Dict = {}
    for path in paths:
        current_level = tree_dict
        for part in path.parts:
            current_level = current_level.setdefault(part, {})

    def build_string(d: Dict, prefix: str = "") -> str:
        lines = []
        entries = sorted(d.keys(), key=lambda k: (not d[k], k.lower()))
        for i, name in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if d[name]:
                new_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(build_string(d[name], new_prefix).splitlines())
        return "\n".join(lines)

    tree_str = f"{root_name}/\n"
    tree_str += build_string(tree_dict)
    return tree_str


# --- Public API ---

def bundle_project(
    project_dir: str,
    output_file: str,
    extra_ignore_patterns: Optional[List[str]] = None,
    use_gitignore: bool = True,
    custom_ignore_file: Optional[str] = None,
) -> None:
    """
    Scans a directory and bundles all non-ignored, non-binary files into a single text file.

    Args:
        project_dir: The root directory of the project to bundle.
        output_file: The path to the output text file.
        extra_ignore_patterns: A list of additional gitignore-style patterns to exclude files.
        use_gitignore: If True, respects the .gitignore file in the project directory.
        custom_ignore_file: Path to a custom file containing ignore patterns.

    Raises:
        FileNotFoundError: If the project_dir does not exist or is not a directory.
    """
    try:
        root_path = Path(project_dir).resolve()
        output_path = Path(output_file).resolve()
    except Exception as e:
        raise ValueError(f"Invalid path provided: {e}") from e

    if not root_path.is_dir():
        raise FileNotFoundError(f"Project directory not found or is not a directory: '{root_path}'")

    if extra_ignore_patterns is None:
        extra_ignore_patterns = []

    custom_ignore_path = Path(custom_ignore_file).resolve() if custom_ignore_file else None

    spec = _get_ignore_spec(root_path, use_gitignore, custom_ignore_path, extra_ignore_patterns)

    included_paths: List[Path] = []
    logger.info(f"Scanning files in '{root_path}'...")
    
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        current_dir_path = Path(dirpath)
        
        dirnames[:] = [d for d in dirnames if not spec.match_file(str(current_dir_path.relative_to(root_path) / d))]

        for filename in filenames:
            file_path = current_dir_path / filename
            
            if file_path == output_path:
                continue

            relative_path = file_path.relative_to(root_path)
            
            if spec.match_file(str(relative_path)):
                continue

            if file_path.suffix.lower() in BINARY_EXTENSIONS:
                logger.debug(f"  - Skip (binary): {relative_path}")
                continue

            included_paths.append(relative_path)
    
    logger.info(f"Found {len(included_paths)} files to include.")
    logger.info(f"Generating output file at '{output_path}'...")

    with open(output_path, "w", encoding="utf-8") as outfile:
        tree_structure = _generate_tree_structure(included_paths, root_path.name)
        outfile.write("<layout>\n")
        outfile.write(tree_structure)
        outfile.write("\n</layout>\n\n")

        for relative_path in sorted(included_paths):
            try:
                full_path = root_path / relative_path
                with open(full_path, "r", encoding="utf-8", errors="ignore") as infile:
                    content = infile.read()
                
                path_str = str(relative_path).replace("\\", "/")
                
                outfile.write(f'<file path="{path_str}">\n')
                outfile.write(content)
                outfile.write("\n</file>\n\n")
                logger.debug(f"  + Add: {relative_path}")
            
            except Exception as e:
                logger.warning(f"  - Error reading {relative_path}: {e}")

    logger.info("Processing complete.")
    logger.info(f"Bundled {len(included_paths)} files into '{output_path}'.")

# --- Command-Line Interface ---

def cli_main():
    """
    The command-line interface entry point.
    """
    parser = argparse.ArgumentParser(
        description="Transforms a project repository into a single, scroll-like text file, respecting ignore rules.",
        epilog="""Examples:
  # Turn the current directory into a scroll named 'combined_output.txt'
  repo2scroll .

  # Specify a project and an output file
  repo2scroll ./my-project -o project_snapshot.txt

  # Exclude all .log and .tmp files
  repo2scroll . --exclude "*.log" "*.tmp"

  # Use a custom ignore file and disable .gitignore
  repo2scroll . --ignore-file .dockerignore --no-gitignore

  # Get verbose output for debugging
  repo2scroll . -v
""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "directory", 
        help="The root directory of the project to bundle."
    )
    parser.add_argument(
        "-o", "--output", 
        default="combined_output.txt",
        help="The name of the output file. (default: combined_output.txt)"
    )
    parser.add_argument(
        "-e", "--exclude",
        nargs='*',
        default=[],
        metavar="PATTERN",
        help="Additional glob patterns to exclude files/directories. Can be specified multiple times."
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Do not use the .gitignore file for exclusion rules."
    )
    parser.add_argument(
        "--ignore-file",
        metavar="FILEPATH",
        help="Path to a custom file with ignore patterns (e.g., .dockerignore)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output for debugging purposes."
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    try:
        bundle_project(
            project_dir=args.directory,
            output_file=args.output,
            extra_ignore_patterns=args.exclude,
            use_gitignore=not args.no_gitignore,
            custom_ignore_file=args.ignore_file
        )
    except (FileNotFoundError, ValueError) as e:
        logger.error(e)
        exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    cli_main()

