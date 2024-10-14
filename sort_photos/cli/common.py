"""Define common Typer objects to be used in CLI commands."""

import os
import re
from typing import Callable
from typing import Optional
from typing import Union

import typer


def path_autocomplete(
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    allow_dash: bool = False,
    match_wildcard: Optional[str] = None,
) -> Callable[[typer.Context, Union[typer.Option, typer.Argument], str], list[str]]:
    """Work-around to fix shell completion for paths with Typer.

    Obtained from: https://github.com/fastapi/typer/discussions/682
    """

    def wildcard_match(string: str, pattern: str) -> bool:
        regex = re.escape(pattern).replace(r"\?", ".").replace(r"\*", ".*")
        return re.fullmatch(regex, string) is not None

    def completer(
        ctx: typer.Context, param: Union[typer.Option, typer.Argument], incomplete: str
    ) -> list[str]:
        items = os.listdir()
        completions = []
        for item in items:
            if not file_okay and os.path.isfile(item):
                continue
            elif not dir_okay and os.path.isdir(item):
                continue

            if readable and not os.access(item, os.R_OK):
                continue
            if writable and not os.access(item, os.W_OK):
                continue

            completions.append(item)

        if allow_dash:
            completions.append("-")

        if match_wildcard is not None:
            completions = filter(lambda i: wildcard_match(i, match_wildcard), completions)

        return [i for i in completions if i.startswith(incomplete)]

    return completer
