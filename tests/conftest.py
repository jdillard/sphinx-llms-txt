"""Pytest configuration for sphinx-llms-txt."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Use Path directly instead of sphinx_path to avoid deprecation warning
from sphinx.testing.util import SphinxTestApp


@pytest.fixture
def rootdir():
    """Get the root directory for test projects."""
    return Path(os.path.dirname(__file__) or ".").absolute() / "roots"


@pytest.fixture
def temp_dir():
    """Create a temporary directory and delete it after the test."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def basic_sphinx_app(temp_dir, rootdir):
    """Create a basic Sphinx app for testing."""
    src_dir = rootdir / "basic"
    app = SphinxTestApp(
        srcdir=src_dir,
        builddir=temp_dir,
        buildername="html",
        freshenv=True,
    )
    yield app

    # Custom cleanup to avoid missing_ok issue
    import sys
    from sphinx.testing.util import _clean_up_global_state

    sys.path[:] = app._saved_path
    _clean_up_global_state()

    # Safe unlink that works with older Python versions
    if hasattr(app, "docutils_conf_path") and app.docutils_conf_path.exists():
        app.docutils_conf_path.unlink()
