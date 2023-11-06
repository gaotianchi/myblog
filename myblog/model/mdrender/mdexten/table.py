import xml.etree.ElementTree as etree

from markdown.extensions.tables import TableExtension, TableProcessor


class CustomTableProcesser(TableProcessor):
    def run(self, parent, blocks):
        """Parse a table block and build table."""
        block = blocks.pop(0).split("\n")
        header = block[0].strip(" ")
        rows = [] if len(block) < 3 else block[2:]

        # Get alignment of columns
        align = []
        for c in self.separator:
            c = c.strip(" ")
            if c.startswith(":") and c.endswith(":"):
                align.append("center")
            elif c.startswith(":"):
                align.append("left")
            elif c.endswith(":"):
                align.append("right")
            else:
                align.append(None)

        # Build table
        table = etree.SubElement(parent, "table")
        table.attrib["class"] = "table table-bordered table-striped table-hover"
        thead = etree.SubElement(table, "thead")
        self._build_row(header, thead, align)
        tbody = etree.SubElement(table, "tbody")
        if len(rows) == 0:
            # Handle empty table
            self._build_empty_row(tbody, align)
        else:
            for row in rows:
                self._build_row(row.strip(" "), tbody, align)

    def _build_row(self, row, parent, align):
        """Given a row of text, build table cells."""
        tr = etree.SubElement(parent, "tr")
        tag = "td"
        if parent.tag == "thead":
            tag = "th"
        cells = self._split_row(row)
        # We use align here rather than cells to ensure every row
        # contains the same number of columns.
        for i, a in enumerate(align):
            c = etree.SubElement(tr, tag)
            if tag == "th":
                c.set("scope", "col")
            try:
                c.text = cells[i].strip(" ")
            except IndexError:  # pragma: no cover
                c.text = ""
            if a:
                if self.config["use_align_attribute"]:
                    c.set("align", a)
                else:
                    c.set("style", f"text-align: {a};")


class CustomTableExtension(TableExtension):
    def extendMarkdown(self, md):
        """Add an instance of `TableProcessor` to `BlockParser`."""
        if "|" not in md.ESCAPED_CHARS:
            md.ESCAPED_CHARS.append("|")
        processor = CustomTableProcesser(md.parser, self.getConfigs())
        md.parser.blockprocessors.register(processor, "table", 75)


def makeExtension(**kwargs):  # pragma: no cover
    return TableExtension(**kwargs)
