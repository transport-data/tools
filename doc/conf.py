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
copyright = "2023–%Y, Transport Data Commons Initiative"
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

GH_URL = "https://github.com/transport-data/tools"

html_css_files = ["css/custom.css"]

html_theme = "furo"

html_logo = "_static/logo.png"

html_theme_options = dict(
    footer_icons=[
        {
            "name": "GitHub",
            "url": GH_URL,
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    top_of_page_buttons=["view", "edit"],
    source_repository=GH_URL,
    source_branch="main",
    source_directory="doc/",
)

html_title = "Tools for the Transport Data Commons (TDC)"

html_static_path = ["_static"]

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
