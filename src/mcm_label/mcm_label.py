from io import BytesIO
import pathlib
from dataclasses import dataclass, field
import pymupdf

from blabel import LabelWriter
from PIL import Image
import io


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
        if target is not None and (
            "png" in (target_path := pathlib.Path(target)).suffix
        ):
            pdf_data = super().write_labels(records, None, extra_stylesheets, base_url)

            if pdf_data is None:
                raise Exception("pdf data returned none")

            convert_pdf_to_png(io.BytesIO(pdf_data), target_path)
            return None

        return super().write_labels(records, target, extra_stylesheets, base_url)


@dataclass
class Part:
    pn: str
    name: str
    image: pathlib.Path


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
            pathlib.Path(__file__).parent / "default_template.html",
            default_stylesheets=(pathlib.Path(__file__).parent / "default_style.css",),
        )

    def render(self):
        for label in self.labels:
            self._writer.write_labels(
                [label.part.__dict__],
                target=self.filename.resolve().parent
                / ("_".join(["label", label.part.pn]) + ".png"),
            )


def main():
    print("main")
