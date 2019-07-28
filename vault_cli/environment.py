import json
import os
import pathlib
from typing import Dict, NoReturn, Optional, Sequence

from vault_cli import types


def make_env_key(base_path: str, path: str, name: str, prefix: Optional[str]) -> str:
    if prefix:
        relative = pathlib.Path(prefix) / pathlib.Path(path).relative_to(
            pathlib.Path(base_path)
        )
    else:
        relative = pathlib.Path(path).relative_to(pathlib.Path(base_path).parent)
    return f"{relative!s}_{name}".upper().replace("/", "_")


def make_env_value(value: types.JSONValue) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value)


def exec_command(command: Sequence[str], environ: Dict[str, str]) -> NoReturn:
    os.execvpe(command[0], tuple(command), environ)
