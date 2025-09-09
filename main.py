from argparse import RawTextHelpFormatter
from argparse import ArgumentParser
from pathlib import Path
import sys


class BlankLinesHelpFormatter(RawTextHelpFormatter):
    def _split_lines(self, text, width):
        return super()._split_lines(text, width) + [""]


class Modes:
    YURI = "yuri"
    SAYORI = "sayori"
    NATSUKI = "natsuki"
    JUST_MONIKA = "monika"
    WORD_POEMS = "poems"
    WORD_POEMS_TEST = "poems-test"

    OPTS_PATH = {YURI, SAYORI, NATSUKI, JUST_MONIKA}
    OPTS_NO_PATH = {WORD_POEMS, WORD_POEMS_TEST}
    DEFAULT = WORD_POEMS


if __name__ == "__main__":
    outdir = "./output"
    tempdir = "./temp"

    Path(outdir).mkdir(exist_ok=True)
    Path(tempdir).mkdir(exist_ok=True)

    parser = ArgumentParser(
        prog="main",
        description="Decodes the *.chr files from DDLC",
        formatter_class=BlankLinesHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)
    nopath = {Modes.WORD_POEMS}

    for opt in Modes.OPTS_PATH:
        sp = subparsers.add_parser(
            opt,
        )
        if opt in {Modes.WORD_POEMS_TEST, Modes.WORD_POEMS}:
            continue
        sp.add_argument(
            "path",
            type=str,
            help="Specifies the *.chr target file",
        )

    for opt in Modes.OPTS_NO_PATH:
        sp = subparsers.add_parser(
            opt,
        )

    pArgs = parser.parse_args()

    match str(pArgs.mode):
        case Modes.YURI:
            from decodeYuri import decode_base64_file

            decode_base64_file(pArgs.path, outdir)

        case Modes.SAYORI:
            from decodeSayori import extract_qr_from_audio

            extract_qr_from_audio(pArgs.path, outdir, tempdir)

        case Modes.NATSUKI:
            from decodeNatsuki import transform_image

            transform_image(pArgs.path, outdir)

        case Modes.JUST_MONIKA:
            from decodeMonika import decode_image

            decode_image(pArgs.path)

        case Modes.WORD_POEMS:
            from poemwords import initPoemsUI

            initPoemsUI(tempdir)

        case Modes.WORD_POEMS_TEST:
            from poemwords import testPoems

            testPoems()
