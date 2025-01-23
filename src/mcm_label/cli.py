from bs4 import BeautifulSoup
import argparse
import pathlib

from mcm_label.mcm_label import Order, Part


def is_valid_file(parser, arg: str) -> pathlib.Path:
    path = pathlib.Path(arg)
    if not path.exists():
        raise parser.error("The file %s does not exist" % path.absolute())
    else:
        if path.is_dir():
            html_files = path.glob("*.html")
            for html in html_files:
                return html
            raise parser.error("No html files found within %s" % path.absolute())
        elif path.suffix == ".html":
            return path
        raise parser.error(
            "Provided path %s is neither a directory nor an html file" % path.absolute()
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "order",
        nargs="?",
        type=lambda x: is_valid_file(parser, x),
        metavar="FILE",
        default=".",
    )
    args = parser.parse_args()

    order = Order(args.order, [], [])

    soup = BeautifulSoup(open(order.filename), "html.parser")
    divs = soup.find_all("div", {"class": "dtl-row-info"})
    for row in divs:
        copy = row.find("div", {"class": "dtl-row-copy"})
        img_container = row.find("div", {"class": "dtl-img-cntnr"})
        img = img_container.find("img", {"src": True})
        img_path = order.filename.parent / pathlib.Path(img.get("src"))
        part = Part(
            copy.find("p", {"class": "dtl-row-specs"}).text.strip(),
            copy.find("p", class_=None).text.strip(),
            img_path,
        )
        order.parts.append(part)

    for part in order.parts:
        print(part)
