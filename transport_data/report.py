"""Generate reports based on data and metadata."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class Report(ABC):
    """Base class for reports."""

    template_name: str

    @abstractmethod
    def render(self) -> Union[str, bytes]: ...

    def render_jinja_template(self, *args, **kwargs) -> str:
        from transport_data.util import jinja2

        env, common = jinja2.get_env()

        return env.get_template(self.template_name).render(*args, **kwargs, **common)

    def rst2odt(self, content: str) -> bytes:
        from docutils.core import publish_string

        from transport_data.util import docutils, jinja2

        env, _ = jinja2.get_env()

        ss_path = Path(env.get_template("odt-styles.xml").filename)
        settings = {"create_links": True, "stylesheet": str(ss_path)}

        # Convert reStructuredText → ODF ODT using docutils
        return publish_string(
            writer=docutils.ODTWriter(), source=content, settings_overrides=settings
        )

    def write_file(self, path: Path) -> None:
        content = self.render()
        if isinstance(content, str):
            path.write_text(content)
        else:
            path.write_bytes(content)
