from collections.abc import Callable
from typing import TypeAlias

PtVector: TypeAlias = tuple[int, int, int]
PtVectorFilter: TypeAlias = Callable[[int, int, int], bool]
WordPointsMaybe: TypeAlias = list[tuple[str, int | None, int | None, int | None]]
WordPointCellRaw: TypeAlias = tuple[str, str, str, str]
WordPointCell: TypeAlias = tuple[str, int, int, int]
WordPoints: TypeAlias = list[WordPointCell]
WordVectorFilter: TypeAlias = Callable[[str, int, int, int], bool]
WordVectorMap: TypeAlias = Callable[[str, int, int, int], WordPointCell]
