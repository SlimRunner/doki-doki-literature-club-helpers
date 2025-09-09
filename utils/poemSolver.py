from PIL import Image, ImageGrab
from dotenv import load_dotenv
from functools import partial
import pygetwindow as gw
import tkinter as tk
import pytesseract
import time
import os

from utils.tableMaker import (
    poemsTransform,
    tabulatePoems,
)
from utils.aliases import (
    WordPoints,
)

load_dotenv()


def findGameWindow():
    title = os.getenv("GAME_TITLE")
    if title is None:
        raise RuntimeError(f"GAME_TITLE key is missing in .env file")
    wins = gw.getWindowsWithTitle(title)
    if not wins:
        raise RuntimeError(f"Could not find window with title {title}")
    return wins[0]


def isWhite(pixel, tol=10):
    """Check if a pixel is 'pure white' within tolerance."""
    r, g, b = pixel
    return abs(r - 255) <= tol and abs(g - 255) <= tol and abs(b - 255) <= tol


def findColumns(img: Image.Image):
    """
    Finds the first blue rule down the middle pixel-column and then
    flood fills left and right to find boundaries.
    """
    w, h = img.size
    pixels = img.load()
    assert pixels is not None
    mid_x = w // 2

    y = 0
    while y < h and not isWhite(pixels[mid_x, y]):
        y += 1

    while y < h and isWhite(pixels[mid_x, y]):
        y += 1

    if y >= h:
        return None, None, None

    left = mid_x
    while left > 0 and not isWhite(pixels[left, y]):
        left -= 1

    right = mid_x
    while right < w - 1 and not isWhite(pixels[right, y]):
        right += 1

    return left, (left + right) // 2, right


def findRows(img: Image.Image):
    """
    Scans down the middle pixel-column and uses the blue rules in the
    paper to find rows
    """
    w, h = img.size
    pixels = img.load()
    assert pixels is not None
    mid_x = w // 2

    y = 0
    row_starts: list[int] = []
    while y < h:
        while y < h and not isWhite(pixels[mid_x, y]):
            y += 1

        while y < h and isWhite(pixels[mid_x, y]):
            y += 1

        if y < h:
            row_starts.append(y)

    return row_starts


def keepBlackOnly(img, tol=100):
    """
    Keep only 'dark' pixels (black text), others → white.
    tol = how close to 0 the RGB values need to be
    """
    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            if r < tol and g < tol and b < tol:
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    return img


def refreshPoemWords(
    poems: WordPoints, winUI: tk.Tk, targetWin: gw.Window, label: tk.Label
):
    targetWin.activate()
    time.sleep(50 / 1000)

    # capture window -> image
    bbox = (
        int(targetWin.left),
        int(targetWin.top),
        int(targetWin.right),
        int(targetWin.bottom),
    )
    gameImage = ImageGrab.grab(bbox)

    columns = findColumns(gameImage)
    assert columns[0] is not None
    l, m, r = columns
    columns = [(l, m), (m, r)]

    rows = findRows(gameImage)
    assert len(rows) == 14
    rows = list(zip(rows[1:11:2], rows[2:11:2]))

    # process image -> image (optional)
    gameImage = keepBlackOnly(gameImage)

    # run OCR on image -> list of words
    yOff = int((rows[0][1] - rows[0][0]) * 0.23)

    idx = 0
    whitelist: list[str] = []
    try:
        for x1, x2 in columns:
            for y1, y2 in rows:
                cellImage = gameImage.crop((x1, y1 + yOff, x2, y2 + yOff))
                # cellImage.save(f"./temp/cap-{idx}.png")
                idx += 1
                word: str = pytesseract.image_to_string(cellImage, lang=OCR_LANG)
                whitelist.append(word.strip().lower().replace(" ", ""))
    except pytesseract.TesseractNotFoundError as err:
        label.config(text="OCR ERROR")
        print(err)
        return

    # TODO: add a way to update the sorter on the fly
    words = poemsTransform(
        poems,
        filter=lambda w, *_: w in whitelist,
        sorter=lambda w, s, n, y: (w, s, n, y),
        # sorter=lambda w, s, n, y: (-y, -n, s, w),
        # sorter=lambda w, s, n, y: (-s, -y, n, w),
        # sorter=lambda w, s, n, y: (-n, -s, y, w),
        # sorter=lambda w, s, n, y: (-y, -n, s, w),
        # sorter=lambda w, s, n, y: (-y, -s, n, w),
    )

    if len(words) != len(whitelist):
        print("A word missed the target. Here is the list detected")
        print(f"included {whitelist}")
        print(
            f"missing {set(w for w, *_ in words).symmetric_difference(set(whitelist))}"
        )

    txt = tabulatePoems(words)
    label.config(text=txt)


def showPoemUI(poems: WordPoints):
    global OCR_LANG
    OCR_LANG = os.getenv("OCR_LANG")
    if OCR_LANG is None:
        raise RuntimeError("OCR_LANG key missing in .env file")

    window = findGameWindow()

    root = tk.Tk()
    root.title("DDLC+ Words")
    root.attributes("-topmost", True)
    root.geometry("+50+100")

    label = tk.Label(root, text="Starting...", font=("Courier New", 10), justify="left")
    buttonClickPartial = partial(refreshPoemWords, poems, root, window, label)
    button = tk.Button(root, text="refresh", width=25, command=buttonClickPartial)

    button.pack()
    label.pack()

    if setUpTesseract():
        root.mainloop()


def setUpTesseract():
    tess_cmd = os.getenv("TESSERACT_CMD")

    if tess_cmd:
        pytesseract.pytesseract.tesseract_cmd = tess_cmd
        return True
    else:
        try:
            _ = pytesseract.get_tesseract_version()
            return True
        except pytesseract.TesseractNotFoundError:
            print("Tesseract not found. Please install or set path in .env")
