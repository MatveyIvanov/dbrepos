import pytest
from sphinx.application import Sphinx

SOURCE_DIR = "docs/source"
CONFIG_DIR = "docs/source"
OUTPUT_DIR = "docs/build"
DOCTREE_DIR = "docs/build/doctrees"


def test_sphinx_html_documentation(self):
    app = Sphinx(
        SOURCE_DIR,
        CONFIG_DIR,
        OUTPUT_DIR,
        DOCTREE_DIR,
        buildername="html",
        warningiserror=True,
    )
    app.build(force_all=True)


def test_sphinx_text_documentation(self):
    app = Sphinx(
        SOURCE_DIR,
        CONFIG_DIR,
        OUTPUT_DIR,
        DOCTREE_DIR,
        buildername="text",
        warningiserror=True,
    )
    app.build(force_all=True)
