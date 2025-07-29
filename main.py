from decodeSayori import extract_qr_from_audio
from decodeYuri import decode_base64_file
from decodeMonika import decode_image
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pathlib import Path
import sys


class BlankLinesHelpFormatter(RawTextHelpFormatter):
    def _split_lines(self, text, width):
        return super()._split_lines(text, width) + [""]


class Character:
    YURI = "yuri"
    SAYORI = "sayori"
    NATSUKI = "natsuki"
    JUST_MONIKA = "monika"

    OPTIONS = {YURI, SAYORI, NATSUKI, JUST_MONIKA}
    DEFAULT = JUST_MONIKA

    def __init__(self, opt: str) -> None:
        if opt not in Character.OPTIONS:
            raise ValueError(f"'{opt}' is not a valid time stamp type")
        self.__options = {o: o == opt for o in Character.OPTIONS}
        self.__selected = opt

    def __repr__(self) -> str:
        return self.__selected


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
    parser.add_argument(
        "character",
        nargs=1,
        type=str,
        choices=Character.OPTIONS,
        help="Specifies the character to attempt to parse.",
    )
    parser.add_argument(
        "file",
        nargs=1,
        type=str,
        help="Specifies the *.chr target file",
    )

    pArgs = parser.parse_args()

    chr_pick = str(pArgs.character[0])
    chr_path = str(pArgs.file[0])

    match chr_pick:
        case Character.YURI:
            result = decode_base64_file(sys.argv[2], outdir)
        case Character.SAYORI:
            result = extract_qr_from_audio(sys.argv[2], outdir, tempdir)
        case Character.NATSUKI:
            parser.error("Not yet implemented")
        case Character.JUST_MONIKA:
            result = decode_image(sys.argv[2])
