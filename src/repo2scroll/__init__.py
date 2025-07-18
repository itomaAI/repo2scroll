# src/repo2scroll/__init__.py

"""
repo2scroll: A versatile tool to transform a project repository into a single, scroll-like text file.
"""

__version__ = "0.1.0"

from .main import bundle_project

# Make the main function available for top-level import
__all__ = ["bundle_project"]

