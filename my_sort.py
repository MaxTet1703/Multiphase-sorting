import csv
import pathlib
from typing import Callable, Optional
from pydantic.types import PathType

CURRENT_PATH = pathlib.Path().cwd()
source = CURRENT_PATH / "file1.csv"
error = CURRENT_PATH / "sdfsdfsf.txt"


def my_sort(src: PathType, output: Optional[PathType] = None, reverse: bool = False,
            key: Optional[Callable] = None) -> None:
    LIMIT_ELEMENT = 40
    if not src.exists():
        raise FileExistsError("File is not exist in the directory")

    files = list(CURRENT_PATH.glob(f'*{src.suffix}'))
    for name in files:
        if name.stem == src.stem:
            files.remove(name)

    if not files:
        for i in range(1, 5):
            new = pathlib.Path(f'file{i}{src.suffix}')
            if new.exists():
                del new
                new = pathlib.Path(f'file{i + 1}{src.suffix}')
            new.touch(mode=0o644)
            files.append(new)

    if output is None:
        output = pathlib.Path(f"response{source.suffix}")
        output.touch(mode=0o644)

    files.append(output)

    distr = [0 if i == len(files) - 1 else 1 for i in range(len(files))]
    empty_series = [0 if i == len(files) - 1 else 1 for i in range(len(files))]

    if src.suffix == ".csv":
        current_line = 1
        LIMIT_ELEMENT += 1
        fieldnames = src.open().readline()
        for f in files:
            f.open(mode="a").write(fieldnames)
    else:
        current_line = 0

    cfile = 0
    loops = 0
    while current_line < LIMIT_ELEMENT:
        if empty_series[cfile] < empty_series[cfile + 1]:
            cfile += 1
        else:
            if empty_series[cfile] == 0:
                loops += 1
                distr0 = distr[0]
                for i in range(len(files) - 1):
                    empty_series[i] = distr0 + distr[i + 1] - distr[i]
                    distr[i] = distr0 + distr[i + 1]
            cfile = 0

        row = src.open().readlines()[current_line]
        files[cfile].open(mode="a").write(row)
        empty_series[cfile] -= 1
        current_line += 1

    if set(empty_series) != {0}:
        distribution(files, empty_series, distr)


def distribution(files: list, empty_series: list, distr: list):
    resum = sum(empty_series)
    cfile = 0
    while resum > 0:
        if empty_series[cfile] < empty_series[cfile + 1]:
            cfile += 1
        else:
            cfile = 0

        files[cfile].open(mode="a").write("none\n")
        resum -= 1
        empty_series[cfile] -=1

