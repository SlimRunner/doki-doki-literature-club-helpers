from collections.abc import Callable
from tabulate import tabulate

from utils.aliases import (
    WordVectorFilter,
    PtVectorFilter,
    WordVectorMap,
    WordPointCell,
    WordPoints,
    PtVector,
)


class TableOptions:
    CHAR_MAJOR = "character"
    AFFINITY_MAJOR = "affinity"


def poemsTransform(
    poems: WordPoints, filter: WordVectorFilter, sorter: WordVectorMap
) -> WordPoints:
    poemsSubset: WordPoints = [wordVec for wordVec in poems if filter(*wordVec)]
    return sorted(poemsSubset, key=lambda t: sorter(*t))


def tabulatePoems(poems: WordPoints):
    header = [
        "#",
        "Word",
        "Sayori",
        "Natsuki",
        "Yuri",
    ]
    rows: list[list[str]] = []

    for i, (word, s, n, y) in enumerate(poems):
        rows.append([str(i), word, str(s), str(n), str(y)])

    tableText = tabulate(rows, header, tablefmt="github")
    return tableText


def writePoemsToTable(poems: WordPoints, path: str):
    wordFilter: PtVectorFilter = lambda s, n, y: (n,) in {(3,)}
    wordSorter: Callable[[WordPointCell]] = lambda x: tuple(x[i] for i in [2, 1, 3, 0])

    words = sorted(filterByValue(poems, wordFilter), key=wordSorter)
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
    tableFile = path

    with open(tableFile, "w") as file:
        file.write(f"# Poem Words ({len(words)})\n\n")
        file.write(tableText)
    print(f"File written to {tableFile}")


def filterByWord(data: WordPoints, filter: Callable[[str], bool]):
    return [(w, s, n, y) for w, s, n, y in data if filter(w)]


def filterByValue(data: WordPoints, filter: PtVectorFilter):
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
