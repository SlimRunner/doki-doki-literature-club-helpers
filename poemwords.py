from collections.abc import Callable
from utils.poemSolver import showPoemUI
import keyboard
import curses
import math
import csv
import os

from utils.aliases import (
    PtVector,
    PtVectorFilter,
    WordPointsMaybe,
    WordPointCellRaw,
    WordPointCell,
    WordPoints,
)


def print_pressed_keys(e: keyboard.KeyboardEvent):
    if e.event_type == "down":
        print(f"scan code: {e.scan_code}")
        # keys = [keyboard._pressed_events[name].name for name in keyboard._pressed_events]
        # print(keys)
        # if "up" in keys:
        #     print("do stuff for up pressed")
        # elif "enter" in keys:
        #     print("do stuff for enter pressed")


# keyboard.hook(print_pressed_keys)


def cursesMain(stdscr: curses.window):
    pass


def intOrNone(text: str) -> int | None:
    try:
        return int(text)
    except:
        return None


def loadPoems(path: str):
    poemWords: list[WordPointCellRaw] = []

    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)

        for i, row in enumerate(reader):
            if i == 0:
                continue
            word, say, nat, yur = row
            poemWords.append((word, say, nat, yur))

    return poemWords


def testPoems():
    origPoems: WordPointsMaybe = []
    plusPoems: WordPoints = []

    intList = lambda w, s, n, y: (str(w), int(s), int(n), int(y))
    intNoneList = lambda w, s, n, y: (str(w), intOrNone(s), intOrNone(n), intOrNone(y))

    origPoems = [
        intNoneList(w, s, n, y)
        for (w, s, n, y) in loadPoems("./data-sets/ddlc-og-poemwords.csv")
    ]
    plusPoems = [
        intList(w, s, n, y)
        for (w, s, n, y) in loadPoems("./data-sets/ddlc-plus-poemwords.csv")
    ]

    from utils.validatePoemwords import validateLegacy

    validateLegacy(origPoems, plusPoems)


def initPoemsUI(tempDir: str):
    plusPoems: WordPoints = []
    intList = lambda w, s, n, y: (str(w), int(s), int(n), int(y))

    plusPoems = [
        intList(w, s, n, y)
        for (w, s, n, y) in loadPoems("./data-sets/ddlc-plus-poemwords.csv")
        if w != "9:15"
    ]

    showPoemUI(plusPoems)
    # writePoemsToTable(plusPoems, os.path.join(tempDir, "poem-table.md"))
    # curses.wrapper(manageUI)
