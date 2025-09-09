from typing import TypeAlias

from utils.aliases import (
    WordPointsMaybe,
    WordPointCell,
    WordPoints,
)


def validateLegacy(src1: WordPointsMaybe, src2: WordPoints):
    assertWordIntegrity(src1, src2)
    assertFavoriteWords(src1, src2)
    assertKnownLikenessVector(src1, src2)


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

    print("integrity passed")


def assertFavoriteWords(src1: WordPointsMaybe, src2: WordPoints):
    A = {w: max(p for p in pts if p is not None) for w, *pts in src1}
    B = {w: max(p for p in pts if p is not None) for w, *pts in src2}

    for key, value in A.items():
        if key in B:
            assert value == B[key]
        else:
            assert False

    print("favorite word passed")


def assertKnownLikenessVector(src1: WordPointsMaybe, src2: WordPoints):
    A = {w: tuple(pts) for w, *pts in src1 if not any(p is None for p in pts)}
    B = {w: tuple(pts) for w, *pts in src2}

    for key, value in A.items():
        if key in B:
            assert value == B[key]
        else:
            assert False

    print("known likeness matches")
