from collections.abc import Callable
from typing import TypeAlias, Any

PtVector: TypeAlias = tuple[int, int, int]
PtVectorFilter: TypeAlias = Callable[[int, int, int], bool]
WordPointsMaybe: TypeAlias = list[tuple[str, int | None, int | None, int | None]]
WordPointCellRaw: TypeAlias = tuple[str, str, str, str]
WordPointCell: TypeAlias = tuple[str, int, int, int]
WordPoints: TypeAlias = list[WordPointCell]
WordVectorFilter: TypeAlias = Callable[[str, int, int, int], bool]
WordVectorMap: TypeAlias = Callable[[Any, Any, Any, Any], WordPointCell]


class Scoreboard:
    def __init__(self):
        self.sayori = 0
        self.natsuki = 0
        self.yuri = 0
        self.words: WordPoints = []

    def add(self, vec: tuple[int, int, int]):
        s, n, y = vec
        self.sayori += s
        self.natsuki += n
        self.yuri += y

    @property
    def packed(self):
        return self.sayori, self.natsuki, self.yuri

    def setWords(self, words: WordPoints):
        self.words = words[:]

    def reset(self):
        self.sayori = 0
        self.natsuki = 0
        self.yuri = 0
