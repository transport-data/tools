"""Generate reports based on data and metadata."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class Report(ABC):
    """Abstract class for reports.

    Subclasses:

    - **must** implement :meth:`render`.
    - **may** use :func:`dataclasses.dataclass` to declare additional attributes and an
      :py:`__init__()` method that accepts and stores them.
    """

    #: Name of a Jinja2 template used by the report; see :meth:`render_jinja_template`.
    template_name: str

    @abstractmethod
    def render(self) -> Union[str, bytes]:
        """Render the report (generate its contents) and return as str or bytes.

        The content may be in any format: plain text, HTML, binary file content, etc.
        """

    def render_jinja_template(self, *args, **kwargs) -> str:
        """Retrieve the Jinja2 :attr:`template_name` and call its render method."""
        from transport_data.util import jinja2

        env, common = jinja2.get_env()

        return env.get_template(self.template_name).render(*args, **kwargs, **common)

    def rst2odt(self, content: str) -> bytes:
        """Convert `content` from reStructuredText to OpenDocument Text (ODT).

        Returns
        -------
        bytes
            The ODT (ZIP) archive.
        """
        from docutils.core import publish_string

        from transport_data.util import docutils, jinja2

        env, _ = jinja2.get_env()

        ss_path = Path(env.get_template("odt-styles.xml").filename)
        settings = {"create_links": True, "stylesheet": str(ss_path)}

        # Convert reStructuredText → ODF ODT using docutils
        return publish_string(
            writer=docutils.ODTWriter(), source=content, settings_overrides=settings
        )

    def write_file(self, path: Path, **kwargs) -> None:
        """:meth:`render` the report and write to `path`."""
        content = self.render()
        if isinstance(content, str):
            path.write_text(content, **kwargs)
        else:
            path.write_bytes(content, **kwargs)
