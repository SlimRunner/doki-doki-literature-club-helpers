from decodeSayori import extract_qr_from_audio
from decodeNatsuki import transform_image
from decodeYuri import decode_base64_file
from decodeMonika import decode_image
from poemwords import initPoemsUI

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

    OPTIONS = {YURI, SAYORI, NATSUKI, JUST_MONIKA, WORD_POEMS}
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

    for opt in Modes.OPTIONS:
        sp = subparsers.add_parser(
            opt,
        )
        sp.add_argument(
            "path",
            type=str,
            help="Specifies the *.chr target file",
        )

    subparsers.add_parser("poems")
    pArgs = parser.parse_args()

    match str(pArgs.mode):
        case Modes.YURI:
            decode_base64_file(pArgs.path, outdir)
        case Modes.SAYORI:
            extract_qr_from_audio(pArgs.path, outdir, tempdir)
        case Modes.NATSUKI:
            transform_image(pArgs.path, outdir)
        case Modes.JUST_MONIKA:
            decode_image(pArgs.path)
        case Modes.WORD_POEMS:
            initPoemsUI(tempdir)
