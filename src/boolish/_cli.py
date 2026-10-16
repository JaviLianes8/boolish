"""Command line interface for boolish."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from typing import TextIO

from boolish._coerce import to_bool
from boolish._errors import BoolishError, NotBooleanError
from boolish._rules import CLASSIC, DEFAULT, MULTILINGUAL, BoolRules
from boolish._version import __version__

_EPILOG = """\
examples:
  boolish yes            prints "true", exits 0
  boolish off            prints "false", exits 1
  boolish --quiet on     prints nothing, exits 0 (read the exit code)
  boolish --lenient Si   folds accents, prints "true"
  boolish --rules multilingual oui
  boolish --true aye --false nay aye
  if boolish --quiet "$FLAG"; then echo enabled; fi

The exit code is 0 when the value is true and 1 when it is false, so the command drops
straight into a shell conditional. An unrecognised value is an error: the message goes
to stderr and the exit code is 2, as for a usage error.
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="boolish",
        description="Convert a boolean-ish value to a real boolean.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("value", help="the value to interpret, for example yes, 0 or off")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict",
        dest="strict",
        action="store_true",
        default=True,
        help="exact vocabulary match only (the default)",
    )
    mode.add_argument(
        "--lenient",
        dest="strict",
        action="store_false",
        help="also fold accents and treat any non-zero number as true",
    )
    parser.add_argument(
        "--rules",
        choices=("classic", "default", "multilingual"),
        default="default",
        help="which built-in vocabulary to use (default: default)",
    )
    parser.add_argument(
        "--true",
        action="append",
        default=[],
        metavar="WORD",
        help="add a word that counts as true (repeatable)",
    )
    parser.add_argument(
        "--false",
        action="append",
        default=[],
        metavar="WORD",
        help="add a word that counts as false (repeatable)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="print nothing; report the result through the exit code only",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"boolish {__version__}",
    )
    return parser


def _resolve_rules(name: str, true: Sequence[str], false: Sequence[str]) -> BoolRules:
    base = {"classic": CLASSIC, "multilingual": MULTILINGUAL}.get(name, DEFAULT)
    if true or false:
        return base.extend(true=true, false=false)
    return base


def _write(stream: TextIO, text: str) -> None:
    """Write a line, escaping what the stream's encoding cannot show."""
    encoding = getattr(stream, "encoding", None) or "ascii"
    safe = text.encode(encoding, "backslashreplace").decode(encoding, "replace")
    try:
        stream.write(safe + "\n")
        stream.flush()
    except OSError:
        # The reader went away (a closed pipe); the exit code still carries the answer.
        # Pointing the descriptor at devnull keeps the interpreter's final flush quiet.
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, stream.fileno())
            os.close(devnull)
        except (OSError, ValueError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line interface and return its exit code.

    Prints ``true`` or ``false`` (unless ``--quiet``) and returns ``0`` for true and
    ``1`` for false. An unrecognised value prints a message to stderr and returns ``2``;
    usage errors exit ``2`` through ``argparse``.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        rules = _resolve_rules(args.rules, args.true, args.false)
    except BoolishError as error:
        _write(sys.stderr, f"boolish: {error}")
        return 2
    try:
        result = to_bool(args.value, rules=rules, strict=args.strict)
    except NotBooleanError as error:
        _write(sys.stderr, f"boolish: {error}")
        return 2
    if not args.quiet:
        _write(sys.stdout, "true" if result else "false")
    return 0 if result else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
