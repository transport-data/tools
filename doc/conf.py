# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

import transport_data  # noqa: F401

if TYPE_CHECKING:
    import sphinx.application

# -- Project information ---------------------------------------------------------------

project = "Tools for the Transport Data Commons (TDC)"
copyright = "2023–2024, Transport Data Commons Initiative"
author = "Transport Data Commons Initiative"

# -- General configuration -------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_autorun",
]
nitpicky = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# A string of reStructuredText included at the beginning of every source file.
rst_prolog = r"""
.. role:: py(code)
   :language: python

.. role:: xml(code)
   :language: xml
"""


def setup(app: "sphinx.application.Sphinx"):
    from sphinx.ext.autosummary.generate import generate_autosummary_docs

    # NB this needs to be here because setup() is executed before the module-level
    #    variables are used
    app.config.templates_path.append("_template")
    generate_autosummary_docs(sources=["api.in"], output_dir="_api", app=app)


# -- Options for HTML output -----------------------------------------------------------

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "_static/logo.png"

html_theme_options = dict(
    logo={"text": project},
    show_navbar_depth=2,
)

html_css_files = ["css/custom.css"]

# -- Options for sphinx.ext.autosummary ------------------------------------------------

autosummary_generate = True

# -- Options for sphinx.ext.extlinks ---------------------------------------------------

extlinks = {
    "issue": ("https://github.com/transport-data/tools/issues/%s", "#%s"),
    "pull": ("https://github.com/transport-data/tools/pull/%s", "PR #%s"),
    "gh-user": ("https://github.com/%s", "@%s"),
}

# -- Options for sphinx.ext.intersphinx ------------------------------------------------

intersphinx_mapping = {
    "click": ("https://click.palletsprojects.com/en/8.1.x/", None),
    "docutils": ("https://sphinx-docutils.readthedocs.io/en/latest", None),
    "dsss": ("https://dsss.readthedocs.io/en/stable", None),
    "jinja2": ("https://jinja.palletsprojects.com/en/3.1.x", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "platformdirs": ("https://platformdirs.readthedocs.io/en/latest/", None),
    "pluggy": ("https://pluggy.readthedocs.io/en/stable", None),
    "pooch": ("https://www.fatiando.org/pooch/latest/", None),
    "py": ("https://docs.python.org/3/", None),
    "pytest": ("https://docs.pytest.org/en/stable/", None),
    "sdmx": ("https://sdmx1.readthedocs.io/en/stable/", None),
}

# -- Options for sphinx.ext.linkcode ---------------------------------------------------

base_path = {
    m: Path(import_module(m).__file__).parents[1]  # type: ignore [arg-type]
    for m in ("transport_data",)
}
base_url = "https://github.com/transport-data/tools/tree/main/"


def linkcode_resolve(domain, info):
    # TODO adjust `base_url` if not on `main` branch
    if domain != "py" or not info["module"]:
        return None

    # Module containing the object
    module = sys.modules[info["module"]]
    # Path of the module relative to the base path of its package
    rel = Path(module.__file__).relative_to(base_path[info["module"].split(".")[0]])

    # The object itself
    try:
        obj = getattr(module, info["fullname"])
    except AttributeError:
        return None
    try:
        # First line number
        firstlineno = obj.__code__.co_firstlineno
    except AttributeError:
        fragment = ""  # A variable, can't obtain the precise location
    else:
        fragment = f"#L{firstlineno}"  # Function, class, or other definition

    return f"{base_url}{rel}{fragment}"


# -- Options for sphinx.ext.napoleon ---------------------------------------------------

napoleon_preprocess_types = True

# -- Options for sphinx.ext.todo -------------------------------------------------------

todo_include_todos = True
