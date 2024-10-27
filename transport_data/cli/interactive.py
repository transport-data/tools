from abc import ABC, abstractmethod
from functools import partial

import click
import prompt_toolkit
from sdmx.model import common, v21

HELP_TEXT = "Control-C: exit"


class Editor(prompt_toolkit.Application):
    def __init__(self, *args, **kwargs) -> None:
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout.containers import HSplit
        from prompt_toolkit.layout.layout import Layout
        from prompt_toolkit.widgets import HorizontalLine, Label, TextArea

        # Build the visual layout
        self.output_field = Label(text=HELP_TEXT, dont_extend_height=False)
        self.input_field = TextArea(
            height=1,
            prompt=">>> ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
        )
        container = HSplit(
            [
                self.output_field,
                HorizontalLine(),
                self.input_field,
                Label(text=HELP_TEXT),
            ]
        )
        layout = Layout(container, focused_element=self.input_field)

        kb = KeyBindings()
        kb.add("c-c")(self._exit)

        super().__init__(key_bindings=kb, layout=layout, full_screen=True)

        # Object to be constructed
        self.ma = v21.DataStructureDefinition()

        # Start with the first View
        self.go_to(MA_Maintainer)

    @staticmethod
    def _exit(event):
        event.app.exit()

    def go_to(self, cls) -> None:
        """Display the :class:`.View` `cls` and its prompt."""
        view = cls()
        self.show_text(view.get_text(self))
        self.input_field.accept_handler = partial(view.accept, app=self)
        self.set_prompt(view.prompt, view.default)

    def set_prompt(self, value: str, default: str = "") -> None:
        """Set the input prompt and default text."""
        from prompt_toolkit.formatted_text import FormattedText
        from prompt_toolkit.layout.processors import BeforeInput

        c = self.input_field.control
        assert c.input_processors and isinstance(c.input_processors[-1], BeforeInput)
        c.input_processors[-1].text = FormattedText([("bold", value + " ")])

        self.input_field.text = default

    def show_text(self, new_text: str) -> None:
        """Show text in the output window."""
        self.output_field.formatted_text_control.text = new_text


class View(ABC):
    """Representation of a :class:`.Editor` view."""

    #: Prompt text to be displayed in the input text area.
    prompt: str
    #: Default input.
    default: str = ""

    @abstractmethod
    def get_text(self, app: "Editor") -> str:
        """Return the text to be displayed in the output text area."""

    @abstractmethod
    def accept(self, buff, *, app: "Editor") -> bool:
        """Handle user input.

        The method **may** inspect :py:`app.input_field.text` to determine what to do.
        """


class MA_Maintainer(View):
    prompt = "Enter the maintainer ID:"
    default = "TDCI"

    def get_text(self, app):
        return f"Creating a new maintainable artefact: {app.ma!r}"

    def accept(self, buff, app):
        app.ma.maintainer = common.Agency(id=app.input_field.text)
        app.go_to(MA_ID)


class MA_ID(View):
    prompt = "Enter its ID:"

    def get_text(self, app):
        return f"Creating a new maintainable artefact: {app.ma!r}"

    def accept(self, buff, app):
        app.ma.id = app.input_field.text
        app.go_to(MA_Version)


class MA_Version(View):
    prompt = "Enter its version:"
    default = "1.0.0"

    def get_text(self, app):
        return f"Creating a new maintainable artefact: {app.ma!r}"

    def accept(self, buff, app):
        app.ma.version = app.input_field.text
        if isinstance(app.ma, common.BaseDataStructureDefinition):
            app.go_to(DSDAddDimension)
        else:  # pragma: no cover
            app.go_to(Save)


def dsd_text(dsd) -> str:
    lines = [f"Creating a new data structure definition: {dsd!r}"]

    for label, cl in (
        ("dimension", dsd.dimensions),
        ("measure", dsd.measures),
        ("attribute", dsd.attributes),
    ):
        lines.extend(["", f"with {len(cl)} {label}(s):"])
        for i, component in enumerate(cl.components, start=1):
            lines.append(f"{i:2}. {component!r}")

    return "\n".join(lines)


class DSDAddDimension(View):
    prompt = "Enter the ID of the next dimension, or [enter] to stop:"

    def get_text(self, app):
        return dsd_text(app.ma)

    def accept(self, buff, app):
        if dim_id := app.input_field.text:
            app.ma.dimensions.getdefault(id=dim_id)
            app.go_to(DSDAddDimension)
        else:
            app.go_to(DSDAddMeasure)


class DSDAddMeasure(View):
    prompt = "Enter the ID of the primary measure, or [enter] to stop:"

    def get_text(self, app):
        return dsd_text(app.ma)

    def accept(self, buff, app):
        if measure_id := app.input_field.text:
            app.ma.measures.getdefault(id=measure_id)
            app.go_to(DSDAddMeasure)
        else:
            app.go_to(DSDAddAttribute)


class DSDAddAttribute(View):
    prompt = "Enter the ID of the next attribute, or [enter] to stop:"

    def get_text(self, app):
        return dsd_text(app.ma)

    def accept(self, buff, app):
        if attr_id := app.input_field.text:
            app.ma.attributes.getdefault(id=attr_id)
            app.go_to(DSDAddAttribute)
        else:
            app.go_to(Save)


class Save(View):
    prompt = "Save? [y/n]"

    def get_text(self, app):
        return f"Creating a new maintainable artefact: {app.ma!r}"

    def accept(self, buff, app):
        if app.input_field.text == "y":
            from transport_data import STORE

            STORE.set(app.ma)
        else:
            pass
        app.exit()


@click.command("edit")
def main():  # pragma: no cover
    "Edit SDMX interactively."
    Editor().run()
