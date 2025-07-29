from collections import deque
from PIL import Image
import numpy as np
import mimetypes
import base64
import magic
import os


def decode_image(file_path):
    img = Image.open(file_path)

    # (left, upper, right, lower)
    crop_box = (330, 330, 470, 470)
    cropped = img.crop(crop_box)

    grayscale = cropped.convert("L")
    blackWhite = grayscale.point(
        lambda x: 0 if x < 128 else 255, mode="1"  # pyright: ignore
    )

    image_bytes = flattenImageToBytes(blackWhite)

    b64Text, isAscii = getAscii(image_bytes)
    outfile = os.path.join("./output", "monika.decoded")

    if isAscii:
        outfile += ".txt"
        b64Text = b64Text.strip("\0 \t\n")
        text, valid = decodeBase64(b64Text)
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(text)
        if valid:
            print(f"ASCII text decoded. Saved to {outfile}")
        else:
            print(f"Not valid ASCII text. Saved as base64 to {outfile}")
    else:
        outfile += ".bin"
        with open(outfile, "wb") as f:
            f.write(image_bytes)
        print(f"Not valid ASCII text. Saved as binary to {outfile}")


def decodeBase64(b64_str: str):
    try:
        raw_data = base64.b64decode(b64_str, validate=True)

        mime = magic.from_buffer(raw_data, mime=True)
        # ext = mimetypes.guess_extension(mime) or ""

        if mime != "text/plain":
            raise TypeError(f"Expected a text MIME type observed {mime}")

        return (raw_data.decode("utf-8"), True)
    except Exception as e:
        return (b64_str, False)


def flattenImageToBytes(image: Image.Image):
    binary_data: list[int] = []
    data = np.array(image)

    bits: deque[int] = deque()
    for row in data:
        bits.extend([1 if pixel else 0 for pixel in row])
        while len(bits) // 8 >= 1:
            byte = 0
            for i in reversed(range(8)):
                byte += (1 << i) * bits.popleft()
            binary_data.append(byte)

    if len(bits) > 0:
        while len(bits) % 8 != 0:
            bits.append(0)
        byte = 0
        for i in reversed(range(8)):
            byte += (1 << i) * bits.popleft()
        binary_data.append(byte)

    return bytes(binary_data)


def reshapedImage(data: bytes, width):
    bitstring = "".join(format(byte, "08b") for byte in data)
    bit_array = np.array([int(b) for b in bitstring], dtype=np.uint8)

    height = len(bit_array) // width
    bit_array = bit_array[: width * height]  # trim excess
    image_data = bit_array.reshape((height, width)) * 255  # scale to 0-255

    img = Image.fromarray(image_data.astype(np.uint8), mode="L")
    return img


def saveReshapedImage(data: bytes):
    outfile = os.path.join("./output", "monika.decoded.png")
    bitstring = "".join(format(byte, "08b") for byte in data)
    bit_array = np.array([int(b) for b in bitstring], dtype=np.uint8)

    # Pick a width that makes the image rectangular and meaningful
    width = 90  # try 64, 128, or 256 — try a few
    height = len(bit_array) // width
    bit_array = bit_array[: width * height]  # trim excess
    image_data = bit_array.reshape((height, width)) * 255  # scale to 0-255

    # Save as image
    img = Image.fromarray(image_data.astype(np.uint8), mode="L")
    img.save(outfile)
    # img.show()


def getAscii(byte_array: bytes):
    try:
        decoded = byte_array.decode("utf-8")
        return (decoded, True)
    except UnicodeDecodeError:
        return ("", False)
