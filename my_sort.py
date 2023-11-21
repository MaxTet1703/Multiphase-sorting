import csv
import pathlib
from typing import Callable, Optional

from pydantic.types import PathType

CURRENT_PATH = pathlib.Path().cwd()
source = CURRENT_PATH / "file1.csv"


def my_sort(src: PathType, output: Optional[PathType] = None, reverse: bool = False,
            key: Optional[Callable] = None) -> None:
    key = str()
    files = list()
    if src.name.endswith("txt"):
        files = list(CURRENT_PATH.glob("*.txt"))
    elif src.name.endswith("csv"):
        files = list(CURRENT_PATH.glob("*.csv"))
    for name in files:
        if name.stem == src.stem:
            files.remove(name)

    print(files)






my_sort(source)
