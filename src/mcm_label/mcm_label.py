from io import BytesIO
import pathlib
from dataclasses import dataclass, field
from blabel.blabel import PRINT_TEMPLATE
import pymupdf

from blabel import LabelWriter, tools
from PIL import Image
import io
import jinja2

THIS_PATH = pathlib.Path(__file__)
DEFAULT_HTML_TEMPLATE = THIS_PATH.parent / "default_template.html"
DEFAULT_STYLESHEET = THIS_PATH.parent / "default_style.css"
DEFAULT_PRINT_TEMPLATE = THIS_PATH.parent / "default_print_template.html"


def write_page_to_png(page: pymupdf.Page, output_path: pathlib.Path):
    # Render the page as a pixmap (image)
    pix = pymupdf.utils.get_pixmap(page, dpi=600)

    # Convert the pixmap to a Pillow Image
    img = Image.open(io.BytesIO(pix.tobytes()))

    # Save the image (You can change the format to PNG or JPEG as needed)
    img.save(output_path, "PNG")


def convert_pdf_to_png(
    pdf: BytesIO | pathlib.Path,
    output_path: pathlib.Path,
    page_number: int | None = None,
):
    with pymupdf.open(pdf) if (type(pdf) is pathlib.Path) else pymupdf.open(
        "pdf", pdf
    ) as doc:
        if page_number is None:
            # Iterate over each page in the PDF
            for page in doc.pages():
                # page = doc.load_page(page_num)

                write_page_to_png(
                    page,
                    output_path.with_stem(
                        "_".join([output_path.stem, str(page.number)])
                    ),
                )
        else:
            page = doc.load_page(page_number)

            write_page_to_png(page, output_path)


class McmLabelWriter(LabelWriter):
    def write_labels(
        self, records: list[dict], target=None, extra_stylesheets=(), base_url=None
    ):
        if target is None:
            return super().write_labels(records, target, extra_stylesheets, base_url)

        target_path = pathlib.Path(target)

        if "png" in target_path.suffix:
            pdf_data = super().write_labels(records, None, extra_stylesheets, base_url)

            if pdf_data is None:
                raise Exception("pdf data returned none")

            convert_pdf_to_png(io.BytesIO(pdf_data), target_path, 0)
            return
        elif "html" in target_path.suffix:
            html = self.records_to_html(records, None, DEFAULT_PRINT_TEMPLATE)
            html = "" if html is None else html
            stylesheets: set[str] = self.default_stylesheets + extra_stylesheets
            if stylesheets:
                links = "".join(
                    [f'<link rel="stylesheet" href="{sheet}">' for sheet in stylesheets]
                )
                html = f"<head>{links}</head>{html}"
            with open(target_path, "w") as f:
                f.write(html)

            return

        return super().write_labels(records, target, extra_stylesheets, base_url)

    def records_to_html(
        self, records, target=None, template: pathlib.Path | None = None
    ):
        """Build the full HTML document to be printed.

        If ``target`` is None, the raw HTML string is returned, else the HTML
        is written at the path specified by ``target``."""
        items_htmls = [self.record_to_html(record) for record in records]
        items_chunks = tools.list_chunks(items_htmls, self.items_per_page)

        if template is None:
            template_obj = PRINT_TEMPLATE
        else:
            with open(template, "r") as f:
                template_obj = jinja2.Template(f.read())

        html = template_obj.render(items_chunks=items_chunks)

        if target is not None:
            with open(target, "w") as f:
                f.write(html)
        else:
            return html


@dataclass
class Part:
    pn: str
    name: str
    image: pathlib.Path
    pn_seq: str = field(init=False)

    def __post_init__(self, *args, **kwargs):
        self.pn_seq = self.pn + "\r1\r"


@dataclass
class Label:
    part: Part


@dataclass
class Order:
    filename: pathlib.Path
    parts: list[Part]
    labels: list[Label]
    _writer: McmLabelWriter = field(init=False)

    def __post_init__(self, *args, **kwargs):
        self._writer = McmLabelWriter(
            DEFAULT_HTML_TEMPLATE,
            default_stylesheets=(DEFAULT_STYLESHEET,),
        )

    def render(self, debug: bool = False):
        if debug:
            print(
                f"Rendering {len(self.labels)} labels to {self.filename.resolve().parent}"
            )

        for label in self.labels:
            records = [label.part.__dict__]
            output_file = self.filename.resolve().parent / (
                "_".join(["label", label.part.pn]) + ".png"
            )

            self._writer.write_labels(records, target=output_file)

            if debug:
                self._writer.write_labels(
                    records, target=output_file.with_suffix(".html")
                )
                self._writer.write_labels(
                    records, target=output_file.with_suffix(".pdf")
                )


def main():
    print("main")
