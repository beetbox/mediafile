import os
import re
import sys
from pathlib import Path

MATCH_VERSION_LINE = re.compile(r"version = \W((\d+\.\d+)\.\d.*?)\W").fullmatch

pyproject = Path(__file__).parent.parent / "pyproject.toml"
version_line_match = next(
    filter(None, map(MATCH_VERSION_LINE, pyproject.read_text().splitlines()))
)
release, version = version_line_match.groups()

sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
]

source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

project = "MediaFile"
copyright = "2016, the beets project"
author = "the beets project"

pygments_style = "sphinx"
htmlhelp_basename = "mediafiledoc"

# LaTeX output.
latex_documents = [
    (
        master_doc,
        "MediaFile.tex",
        "MediaFile Documentation",
        "the beets project",
        "manual",
    ),
]

# mapage output.
man_pages = [(master_doc, "mediafile", "MediaFile Documentation", [author], 1)]
