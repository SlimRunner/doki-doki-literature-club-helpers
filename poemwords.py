from collections.abc import Callable
from tabulate import tabulate
from typing import TypeAlias
import keyboard
import curses
import math
import csv
import os

PtVector: TypeAlias = tuple[int, int, int]
PtVectorFilter: TypeAlias = Callable[[int, int, int], bool]
WordPointsMaybe: TypeAlias = list[tuple[str, int | None, int | None, int | None]]
WordPointCell: TypeAlias = tuple[str, int, int, int]
WordPoints: TypeAlias = list[WordPointCell]


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


def compareData():
    pass


def initPoemsUI(tempDir):
    ogData: WordPointsMaybe = []
    plusData: WordPoints = []

    with open("./data-sets/ddlc-og-poemwords.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)

        for i, row in enumerate(reader):
            if i == 0:
                continue
            word, say, nat, yur = row
            say, nat, yur = (None if n == "?" else int(n) for n in (say, nat, yur))
            ogData.append((word, say, nat, yur))

    with open("./data-sets/ddlc-plus-poemwords.csv", newline="") as csvfile:
        reader = csv.reader(csvfile)

        for i, row in enumerate(reader):
            if i == 0:
                continue
            word, say, nat, yur = row
            say, nat, yur = (int(n) for n in (say, nat, yur))
            plusData.append((word, say, nat, yur))

    assertWordIntegrity(ogData, plusData)
    assertFavoriteWords(ogData, plusData)
    assertKnownLikenessVector(ogData, plusData)

    wordFilter: PtVectorFilter = lambda s, n, y: True
    wordSorter: Callable[[WordPointCell]] = lambda x: (x[3], x[2], x[1], x[0])

    words = sorted(filterWords(plusData, wordFilter), key=wordSorter)
    header = [
        "Word",
        "Loves",
        "Likes",
        "Dislikes",
        "Hates",
    ]
    rows: list[list[str]] = []

    for word, s, n, y in words:
        rows.append([word, *(", ".join(ptv) for ptv in rankPtVector((s, n, y)))])

    tableText = tabulate(rows, header, tablefmt="github")
    tableFile = os.path.join(tempDir, "poem-table.md")

    with open(tableFile, "w") as file:
        file.write(f"# Poem Words ({len(words)})\n\n")
        file.write(tableText)
    print(f"File written to {tableFile}")
    # curses.wrapper(manageUI)


def stateIdle():
    pass


def stateExit():
    pass


def editingQuery():
    pass


def validatingQuery():
    pass


def typeaheadStart():
    pass


def typeaheadAccumulating():
    pass


def assertWordIntegrity(src1: WordPointsMaybe, src2: WordPoints):
    A = set(w for w, _, _, _ in src1)
    B = set(w for w, _, _, _ in src2)
    assert len(A) == len(src1)
    assert len(B) == len(src2)

    AdiffB = A.difference(B)
    assert len(AdiffB) == 0

    BdiffA = B.difference(A)
    assert len(BdiffA) == 1
    assert "9:15" in BdiffA


def assertFavoriteWords(src1: WordPointsMaybe, src2: WordPoints):
    A = {w: max(p for p in pts if p is not None) for w, *pts in src1}
    B = {w: max(p for p in pts if p is not None) for w, *pts in src2}

    for key, value in A.items():
        if key in B:
            assert value == B[key]
        else:
            assert False


def assertKnownLikenessVector(src1: WordPointsMaybe, src2: WordPoints):
    A = {w: tuple(pts) for w, *pts in src1 if not any(p is None for p in pts)}
    B = {w: tuple(pts) for w, *pts in src2}

    for key, value in A.items():
        if key in B:
            assert value == B[key]
        else:
            assert False


def filterWords(data: WordPoints, filter: PtVectorFilter):
    return [(w, s, n, y) for w, s, n, y in data if filter(s, n, y)]


def rankPtVector(vector: PtVector):
    ranked = parsePtVector(vector)

    vecList: list[list[str]] = [[] for _ in range(4)]

    for girl in ["sayori", "natsuki", "yuri"]:
        vecList[ranked[girl]] += [girl]

    return list(reversed(vecList))


def parsePtVector(vector: PtVector):
    sayori, natsuki, yuri = vector

    return {
        "sayori": sayori,
        "natsuki": natsuki,
        "yuri": yuri,
    }
