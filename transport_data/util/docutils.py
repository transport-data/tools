"""Utilities for :mod:`docutils`."""

from pathlib import Path
from zipfile import BadZipFile, ZipFile

import docutils.writers
import docutils.writers.odf_odt
from docutils.writers.odf_odt import SubElement


class ODFTranslator(docutils.writers.odf_odt.ODFTranslator):
    """Translator from docutils DOM to OpenDocumentText

    This subclass works around bugs and missing figures in the upstream class.

    - Tolerate a file path with ".xml" for the "stylesheet" setting.
    - Fix internal hyperlinks:

      - Write internal hyperlink targets as :xml:`<text:bookmark>` instead of
        :xml:`<text:reference-mark>`.
      - Write hyperlinks to internal targets as :xml:`<text:a>` instead of
        :xml:`<text:reference-ref>`. The latter does not allow to specify the text
        content of the reference. In this class, the reference text is as given in the
        docutils DOM source.
    """

    # NB Lines excluded with "pragma: no cover" are not used in transport_data

    pending_ids: list[str]

    def retrieve_styles(self, extension: str) -> None:
        """Retrieve the stylesheet a file with extension either ".xml" or `extension`.

        Returns nothing.
        """
        from lxml import etree

        stylespath = Path(self.settings.stylesheet)

        if stylespath.suffix == ".xml":
            with open(stylespath, "rb") as stylesfile:
                self.str_stylesheet = stylesfile.read()
        elif stylespath.suffix == extension:  # pragma: no cover
            with ZipFile(stylespath) as zf:
                self.str_stylesheet = zf.read("styles.xml")
                self.str_stylesheetcontent = zf.read("content.xml")
        else:  # pragma: no cover
            raise RuntimeError(
                f"stylesheet path {stylespath} must be {extension} or .xml file"
            )

        self.dom_stylesheet = etree.fromstring(self.str_stylesheet)

        if self.str_stylesheetcontent:  # pragma: no cover
            # TODO Identify what this is for, or remove
            self.dom_stylesheetcontent = etree.fromstring(self.str_stylesheetcontent)
            self.table_styles = self.extract_table_styles(self.str_stylesheetcontent)

    def append_pending_ids(self, el) -> None:
        if self.settings.create_links:
            for id in self.pending_ids:
                SubElement(el, "text:bookmark", attrib={"text:name": id})
        self.pending_ids.clear()

    def visit_reference(self, node: "docutils.nodes.reference") -> None:
        # text = node.astext()
        if self.settings.create_links:
            if "refuri" in node:
                href = node["refuri"]
                if self.settings.cloak_email_addresses and href.startswith(
                    "mailto:"
                ):  # pragma: no cover
                    href = self.cloak_mailto(href)
                el = self.append_child(
                    "text:a",
                    attrib={
                        "xlink:href": "%s" % href,
                        "xlink:type": "simple",
                    },
                )
                self.set_current_element(el)
            elif "refid" in node:
                el2 = self.append_child(
                    "text:a",
                    attrib={"xlink:type": "simple", "xlink:href": f"#{node['refid']}"},
                )
                el2.text = node.children.pop(0)
            else:  # pragma: no cover
                self.document.reporter.warning(
                    'References must have "refuri" or "refid" attribute.'
                )
        if (
            self.in_table_of_contents
            and len(node.children) >= 1
            and isinstance(node.children[0], docutils.nodes.generated)
        ):  # pragma: no cover
            node.remove(node.children[0])


class ODTWriter(docutils.writers.odf_odt.Writer):
    """Docutils writer for OpenDocument Text.

    This subclass works around bugs in the upstream class.
    """

    # NB Lines excluded with "pragma: no cover" are not used in transport_data

    def __init__(self):
        docutils.writers.Writer.__init__(self)
        # Use the ODFTranslator subclass defined in this module
        self.translator_class = ODFTranslator

    def copy_from_stylesheet(self, outzipfile: "ZipFile") -> None:
        """Copy images, settings, etc from the stylesheet doc into target doc."""
        stylespath = Path(self.settings.stylesheet)

        try:
            zf = ZipFile(stylespath)
        except BadZipFile:
            # `stylespath` references a non-ODF archive, which will not contain
            # settings.xml or any Pictures/ directory. Copy these instead from the
            # default file.
            zf = ZipFile(self.default_stylesheet_path)

        # Copy the styles
        self.write_zip_str(outzipfile, "settings.xml", zf.read("settings.xml"))

        # Copy the images
        for name in filter(
            lambda n: n.startswith("Pictures/"), zf.namelist()
        ):  # pragma: no cover
            outzipfile.writestr(name, zf.read(name))
