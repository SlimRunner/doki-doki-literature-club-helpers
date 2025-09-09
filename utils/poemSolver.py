from PIL import Image, ImageGrab, ImageFilter
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
    Scoreboard,
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


def updateScores(lblScores: tk.Label, scores: tuple[int, int, int]):
    lblText = ", ".join(f"{n}: {v}" for (n, v) in zip(["Say", "Nat", "Yur"], scores))
    lblScores.config(text=lblText)


def addScore(lblScores: tk.Label, scores: Scoreboard, event: tk.Event):
    if event.keysym == "Return" and isinstance(event.widget, tk.Entry):
        txtEntry = event.widget
        try:
            index = int(txtEntry.get())
            entry = scores.words[index]
            scores.add(entry[1:])
            updateScores(lblScores, scores.packed)
        except IndexError as err:
            print("index out of range")
        except ValueError:
            print("invalid integer")
        txtEntry.delete(0, tk.END)


def resetTallies(lblScores: tk.Label, scores: Scoreboard):
    scores.reset()
    updateScores(lblScores, scores.packed)


def refreshPoemWords(
    poems: WordPoints,
    winUI: tk.Tk,
    targetWin: gw.Window,
    lblTable: tk.Label,
    lblScores: tk.Label,
    scores: Scoreboard,
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

    # detect rows and columns
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

    replList = {"scafs": "scars"}

    idx = 0
    whitelist: list[str] = []
    try:
        for x1, x2 in columns:
            for y1, y2 in rows:
                cellImage = gameImage.crop((x1, y1 + yOff, x2, y2 + yOff))
                cellImage = cellImage.filter(ImageFilter.GaussianBlur(radius=0.8))
                idx += 1
                word: str = pytesseract.image_to_string(cellImage, lang=OCR_LANG)
                word = word.strip().lower().replace(" ", "")
                correction = replList[word] if word in replList else None
                if correction is not None:
                    print(f"correction happened: {word} -> {correction}")
                    cellImage.save(f"./temp/cap-{idx}.png")
                    print(f"saved image: ./temp/cap-{idx}.png")
                    word = correction
                whitelist.append(word)
    except pytesseract.TesseractNotFoundError as err:
        lblTable.config(text="OCR ERROR")
        print(err)
        return

    # TODO: add a way to update the sorter on the fly
    words = poemsTransform(
        poems,
        filter=lambda w, *_: w in whitelist,
        sorter=lambda w, s, n, y: (w, s, n, y),
        # sorter=lambda w, s, n, y: (-s, -n, y, w),
        # sorter=lambda w, s, n, y: (-s, -y, n, w),
        # sorter=lambda w, s, n, y: (-n, -s, y, w),
        # sorter=lambda w, s, n, y: (-n, -y, s, w),
        # sorter=lambda w, s, n, y: (-y, -n, s, w),
        # sorter=lambda w, s, n, y: (-y, -s, n, w),
    )

    scores.setWords(words)

    if len(words) != len(whitelist):
        print("A word missed the target. Here is the list detected")
        print(f"included {whitelist}")
        diffSet = set(w for w, *_ in words).symmetric_difference(set(whitelist))
        print(f"missing {diffSet}")

    lblTable.config(text=tabulatePoems(words))
    updateScores(lblScores, scores.packed)


def showPoemUI(poems: WordPoints):
    global OCR_LANG
    OCR_LANG = os.getenv("OCR_LANG")
    if OCR_LANG is None:
        raise RuntimeError("OCR_LANG key missing in .env file")

    window = findGameWindow()

    root = tk.Tk()
    root.title("DDLC+ Words")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    root.geometry("+50+100")

    scores = Scoreboard()

    lblTable = tk.Label(
        root, text="Starting...", font=("Courier New", 10), justify="left"
    )
    lblScores = tk.Label(
        root, text="scores...", font=("Courier New", 10), justify="left"
    )
    refreshClickPartial = partial(
        refreshPoemWords, poems, root, window, lblTable, lblScores, scores
    )
    btnRefresh = tk.Button(
        root, text="read words", width=25, command=refreshClickPartial
    )
    resetClickPartial = partial(resetTallies, lblScores, scores)
    btnReset = tk.Button(root, text="reset", width=10, command=resetClickPartial)
    txtEntry = tk.Entry(root, width=5)

    btnRefresh.pack()
    lblTable.pack()
    txtEntry.pack()
    lblScores.pack()
    btnReset.pack()

    entryKeyPartial = partial(addScore, lblScores, scores)
    txtEntry.bind("<KeyRelease>", entryKeyPartial)

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
