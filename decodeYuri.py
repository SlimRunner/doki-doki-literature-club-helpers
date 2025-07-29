from pathlib import Path
import mimetypes
import base64
import imghdr
import magic
import sys


def decode_base64_file(input_path, outdir="output"):
    try:
        with open(input_path, "r") as f:
            b64_str = f.read().strip()
        raw_data = base64.b64decode(b64_str, validate=True)
    except Exception as e:
        print(f"Failed to decode base64 from file: {e}", file=sys.stderr)
        raise e

    mime = magic.from_buffer(raw_data, mime=True)
    ext = mimetypes.guess_extension(mime)

    if ext is None:
        img_type = imghdr.what(None, h=raw_data)
        if img_type:
            ext = f".{img_type}"
            mime = f"image/{img_type}"

    print(f"Detected MIME type: {mime}, extension: {ext or 'unknown'}")

    output_path = Path(outdir) / f"yuri.decoded{ext or '.bin'}"
    with open(output_path, "wb") as f:
        f.write(raw_data)

    print(f"Saved decoded content to: {output_path}")
