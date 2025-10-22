"Edit SDMX interactively."

from abc import ABC, abstractmethod
from math import ceil, log10
from typing import cast

import click
import prompt_toolkit
from sdmx.model import common, v21

#: Kinds of :class:`.MaintainableArtefacts` that can be edited.
CLASSES = (
    common.AgencyScheme,  # 1
    common.Codelist,  # 2
    common.ConceptScheme,  # 3
    v21.DataflowDefinition,  # 4
    v21.DataStructureDefinition,  # 5
)

HELP_TEXT = "Control-C: exit"


class EditorState:
    """References to artefacts being created or edited."""

    ia: common.IdentifiableArtefact | None = None
    na: common.NameableArtefact | None = None
    ma: common.MaintainableArtefact | None = None

    view: "View | None" = None


class Editor(prompt_toolkit.Application):
    """:class:`prompt_toolkit.Application` for editing SDMX maintainable artefacts.

    The editor has a simple UI with an output pane and a configurable prompts. These are
    set by :class:`.View` subclasses, which each implement :meth:`.View.accept` to
    accept and handle user input. Transitions between views are mainly described by
    :data:`FLOW`.
    """

    current: EditorState

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
            accept_handler=self.accept,
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

        # Connect keybindings
        kb = KeyBindings()
        kb.add("c-c")(self._exit)

        # State for other classes in this module
        self.current = EditorState()

        # Construct the Application
        super().__init__(key_bindings=kb, layout=layout, full_screen=True)

        # Start with the first View in FLOW
        self.next()

    @staticmethod
    def _exit(event):
        """Control-C handler."""
        event.app.exit()

    def next(self, view: type["View"] | None = None) -> None:
        """Identify the next :class:`.View` `cls`; display it and its prompt.

        If `view` is :any:`None` (the default), :data:`FLOW` is used to identify the
        class.
        """

        # Look up the next view using FLOW
        if self.current.view is None:
            cls: type["View"] = cast(type["View"], FLOW[None])
            assert isinstance(cls, type)
        elif view is None:
            # No view
            class_or_map = FLOW[type(self.current.view)]
            obj = self.current.ia
            if class_or_map is None:
                # Exit the application
                self.exit()
                return
            elif isinstance(class_or_map, type):
                cls = class_or_map
            else:
                try:
                    cls = [c for t, c in class_or_map.items() if isinstance(obj, t)][0]
                except IndexError:  # pragma: no cover
                    raise RuntimeError(
                        f"No view to follow {type(self.current.view)} among "
                        f"{class_or_map}"
                    )
        else:
            cls = view

        # Create the next view
        self.current.view = cls(self)

    def accept(self, buff) -> bool:
        """Handle input to the input_field."""
        # Call the accept() method on the current View
        assert self.current.view
        cls = self.current.view.accept(self.input_field.text)
        # Pass the class of the next View (if any was returned) to .next()
        self.next(cls)

        return True

    def set_prompt(self, value: str, default: str = "") -> None:
        """Set the input prompt and default text."""
        from prompt_toolkit.formatted_text import FormattedText
        from prompt_toolkit.layout.processors import BeforeInput

        c = self.input_field.control
        assert c.input_processors and isinstance(c.input_processors[-1], BeforeInput)
        c.input_processors[-1].text = FormattedText([("bold", value + " ")])

        self.input_field.text = default
        self.input_field.buffer.cursor_position = len(default)


class View(ABC):
    """Representation of a :class:`.Editor` view."""

    #: Reference to the Editor.
    app: Editor
    #: Reference to the EditorState.
    current: EditorState

    #: Text to be displayed in the output text area.
    text: str
    #: Prompt text to be displayed in the input text area.
    prompt: str
    #: Default input.
    default: str = ""

    def __init__(self, app) -> None:
        """Create and display the view.

        Subclasses **may** override this method, but **must** call
        :py:`super().__init__(app)`.
        """
        self.app = app
        self.current = app.current

        # Display the view
        app.output_field.formatted_text_control.text = self.text
        app.set_prompt(self.prompt, self.default)

    @abstractmethod
    def accept(self, text: str) -> type["View"] | None:
        """Handle user input.

        Subclasses **must** implement this method. An implementation **may** return a
        :class:`.View` subclass (not instance) to indicate the next View to be
        displayed; if it returns :any:`None`, then :data:`NEXT_VIEW` is used to identify
        the next View.
        """


# Concrete View subclasses, in alphabetical order


class ComponentListEdit(View):
    """Base class for editing a :class:`.ComponentList` on ."""

    _cl_name = ""

    def __init__(self, app):
        # Reference to the ComponentList
        self._component_list = getattr(app.current.ma, self._cl_name + "s")
        self.prompt = f"Enter the ID of the next {self._cl_name}, or [enter] to stop:"

        super().__init__(app)

    @property
    def text(self):
        return dsd_text(self.current.ma)

    def accept(self, text):
        if text:
            self._component_list.getdefault(id=text)
            return type(self)  # Add another component
        else:
            return None  # Next view according to FLOW


class DFDStructureURN(View):
    """Set :attr:`.BaseDataflowDefinition.structure` based on the URN of a DSD."""

    @property
    def text(self):
        lines = [
            f"Creating a new data flow definition: {self.current.ma!r}\n",
            "Enter the full or partial URN for the data structure definition (DSD).",
        ]
        return "\n".join(lines)

    prompt = "Enter the URN:"

    def accept(self, text):
        from transport_data import STORE

        try:
            dsd = STORE.get(text)
        except KeyError:  # pragma: no cover  # TODO Extend tests to cover this error
            return DFDStructureURN
        self.current.ma.structure = dsd


class DSDAddDimension(ComponentListEdit):
    _cl_name = "dimension"


class DSDAddMeasure(ComponentListEdit):
    _cl_name = "measure"


class DSDAddAttribute(ComponentListEdit):
    _cl_name = "attribute"


class IA_ID(View):
    """:attr:`.IdentifiableArtefact.id`."""

    @property
    def text(self):
        return f"Creating a new artefact: {self.current.ia!r}"

    prompt = "Enter its ID:"

    def accept(self, text):
        self.current.ia.id = text


class ItemSchemeEdit(View):
    """Edit a :class:`.ItemScheme`."""

    def __init__(self, app):
        current = app.current
        if isinstance(current.na, current.ma._Item):
            # Adding an item to an ItemScheme. Store and clear.
            current.ma.append(current.na)
            current.ia = current.na = current.ma

        super().__init__(app)

    @property
    def text(self):
        ma = self.current.ma
        lines = [
            f"Creating a new {type(ma).__name__}: {ma!r}\n",
            f"containing {len(ma)} {ma._Item.__name__}(s):\n",
        ]

        # List the items
        width = ceil(log10(len(ma) + 1))
        for i, item in enumerate(ma.items.values(), start=1):
            lines.append(f"{i:{width}}. {item!r}")

        return "\n".join(lines)

    prompt = "Enter a number to edit; [n]ew item; or [enter] to stop:"

    def accept(self, text):
        if text == "n":  # New Item
            self.current.ia = self.current.na = self.current.ma._Item()
        elif text == "":  # Done adding Items; save
            return MA_Save
        else:
            try:
                # Interpret `text` as the number of an Item
                i = int(text)
                self.current.ia = self.current.na = list(
                    self.current.ma.items.values()
                )[i - 1]
            except (
                ValueError,  # Not an integer
                IndexError,  # Not an integer that is the index of an existing Item
            ):
                return type(self)


class MA_Class(View):
    """Class for a :class:`.MaintainableArtefact`."""

    prompt = "Enter a number from the above list:"

    @property
    def text(self):
        lines = [
            "Creating a new maintainable artefact.\n",
            "Choose a class from among:\n",
        ]
        for i, cls in enumerate(CLASSES, start=1):
            lines.append(f"{i:2}. {cls.__module__}.{cls.__name__}")
        return "\n".join(lines)

    def accept(self, text):
        try:
            ma_class = CLASSES[int(text) - 1]
            self.current.ia = self.current.na = self.current.ma = (
                ma_class()
            )  # Create the object to be constructed
        except (
            ValueError,  # Non-integer input
            IndexError,  # A value that is not in the enumeration of `choices`
        ):
            return type(self)  # Repeat the same view


class MA_Maintainer(View):
    """:attr:`.MaintainableArtefact.maintainer`."""

    @property
    def text(self):
        return f"Creating a new artefact: {self.current.ma!r}"

    prompt = "Enter the maintainer ID:"
    default = "TDCI"

    def accept(self, text):
        self.current.ma.maintainer = common.Agency(id=text)


class MA_Save(View):
    """Save a completed :class:`.MaintainableArtefact`."""

    @property
    def text(self):
        return f"Creating a new artefact: {self.current.ma!r}"

    prompt = "Save? [y/n]"

    def accept(self, text):
        if text != "y":
            return

        from transport_data import STORE

        STORE.set(self.current.ma)


class NA_Name(View):
    """:attr:`.NameableArtefact.name`."""

    prompt = "Enter its name or [enter] to skip:"

    @property
    def text(self):
        return f"Creating a new artefact: {self.current.na!r}"

    def accept(self, text):
        if text:
            self.current.na.name = text


class VA_Version(View):
    """:attr:`.VersionableArtefact.version`."""

    @property
    def text(self):
        return f"Creating a new artefact: {self.current.ma!r}"

    prompt = "Enter its version:"
    default = "1.0.0"

    def accept(self, text):
        self.current.ma.version = text


#: Mapping from Views to the following View to be displayed.
#:
#: If the value is a :class:`dict`, it maps from classes for :attr:`.EditorState.ia` to
#: Views.
FLOW: dict[type[View] | None, None | type[View] | dict[type, type[View]]] = {
    None: MA_Class,
    MA_Class: MA_Maintainer,
    MA_Maintainer: IA_ID,
    IA_ID: NA_Name,
    NA_Name: {
        common.Item: ItemSchemeEdit,
        common.VersionableArtefact: VA_Version,
    },
    VA_Version: {
        common.BaseDataStructureDefinition: DSDAddDimension,
        common.BaseDataflow: DFDStructureURN,
        common.ItemScheme: ItemSchemeEdit,
    },
    DFDStructureURN: MA_Save,
    DSDAddDimension: DSDAddMeasure,
    DSDAddMeasure: DSDAddAttribute,
    DSDAddAttribute: MA_Save,
    ItemSchemeEdit: IA_ID,
    MA_Save: None,
}


def dsd_text(dsd: v21.DataStructureDefinition) -> str:
    """Generate display text about a DSD."""
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


@click.command("edit", help=__doc__)
def main():  # pragma: no cover
    Editor().run()
