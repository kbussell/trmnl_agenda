import argparse
import io
import os
import xml.etree.ElementTree as ET
from base64 import b64encode

from cairosvg import svg2png

ET.register_namespace("", "http://www.w3.org/2000/svg")


def make_encoded_png(input_filename, out_size):
    tree = ET.parse(input_filename)
    svg = tree.getroot()
    svg.attrib["width"] = f"{out_size}px"
    svg.attrib["height"] = f"{out_size}px"

    buffer = io.BytesIO()
    tree.write(buffer)

    return b64encode(svg2png(buffer.getvalue()))


def make_png_dict(input_dir, out_size):
    png_dict = {}
    for filename in os.listdir(input_dir):
        filename = filename.lower()
        if filename.endswith(".svg"):
            key = filename.rsplit(".", 1)[0]
            b64png = make_encoded_png(os.path.join(input_dir, filename), out_size)
            png_dict[key] = b64png.decode("ascii")

    return png_dict


def dump_css_styles(png_dict):
    css_styles = []

    for key, value in png_dict.items():
        css_styles.extend(
            [
                f"  .{key} {{",
                f"    background: url(data:img/png;base64,{value});",
                "  }",
            ]
        )

    return "\n".join(css_styles)


def main():
    parser = argparse.ArgumentParser(description="Create a css file of weather icons")
    parser.add_argument("input_dir", type=str, help="Input directory of weather icons")
    parser.add_argument("output_file", type=str, help="Output css file name")
    parser.add_argument("-s", "--size", type=int, help="Output size in pixels", default=60)
    args = parser.parse_args()

    png_dict = make_png_dict(args.input_dir, args.size)
    with open(os.path.join(os.getcwd(), args.output_file), "w") as f:
        f.write(dump_css_styles(png_dict))


if __name__ == "__main__":
    main()
