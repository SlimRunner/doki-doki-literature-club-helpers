import base64
import binascii
import imghdr
import mimetypes
import magic  # pip install python-magic
from pathlib import Path


def analyze_base64_file(input_path, output_dir="output"):
    try:
        with open(input_path, "r") as f:
            b64_str = f.read().strip()
        raw_data = base64.b64decode(b64_str, validate=True)
    except Exception as e:
        return f"Failed to decode base64 from file: {e}"

    mime = magic.from_buffer(raw_data, mime=True)
    ext = mimetypes.guess_extension(mime) or ""

    if not ext:
        img_type = imghdr.what(None, h=raw_data)
        if img_type:
            ext = f".{img_type}"
            mime = f"image/{img_type}"

    print(f"Detected MIME type: {mime}, extension: {ext or 'unknown'}")

    Path(output_dir).mkdir(exist_ok=True)
    output_path = Path(output_dir) / f"yuri.decoded{ext or '.bin'}"
    with open(output_path, "wb") as f:
        f.write(raw_data)

    return f"Saved decoded content to: {output_path}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyze_base64.py <base64_file>")
    else:
        result = analyze_base64_file(sys.argv[1])
        print(result)
