# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information ---------------------------------------------------------------

project = "TDC tools"
copyright = "2023, Transport Data Commons Initiative"
author = "Transport Data Commons Initiative"

# -- General configuration -------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.todo",
]

templates_path = ["_template"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -----------------------------------------------------------

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "_static/logo.png"

html_theme_options = {"logo": {"text": project}}

html_css_files = ["css/custom.css"]


# -- Options for sphinx.ext.intersphinx ------------------------------------------------

intersphinx_mapping = {
    # "click": ("https://click.palletsprojects.com/en/8.1.x/", None),
    "pooch": ("https://www.fatiando.org/pooch/latest/", None),
    "py": ("https://docs.python.org/3/", None),
    "pytest": ("https://docs.pytest.org/en/stable/", None),
    "sdmx": ("https://sdmx1.readthedocs.io/en/stable/", None),
}

# -- Options for sphinx.ext.linkcode ---------------------------------------------------


def linkcode_resolve(domain, info):
    if domain != "py" or not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    # FIXME this does not work when there is an __init__.py in a submodule
    return f"https://github.com/transport-data/tools/tree/main/{filename}.py"
