import csv
import pathlib
from typing import Callable, Optional
from pydantic.types import PathType

CURRENT_PATH = pathlib.Path().cwd()
source = CURRENT_PATH / "file1.csv"
error = CURRENT_PATH / "sdfsdfsf.txt"


def my_sort(src: PathType, output: Optional[PathType] = None, reverse: bool = False,
            key: Optional[Callable] = None, LIMIT_ELEMENT=40) -> None:
    src = CURRENT_PATH / src
    if not src.exists():
        raise FileExistsError("File is not exist in the directory")

    if output is None:
        output = pathlib.Path(CURRENT_PATH / f"response{source.suffix}")
        output.touch(mode=0o644)
    else:
        output = CURRENT_PATH / output

    files = [file for file in CURRENT_PATH.glob(f'*{src.suffix}') if file.name not in (src.name, output.name)]
    if not files:
        for i in range(1, 5):
            new = pathlib.Path(f'file{i}{src.suffix}')
            if new.exists():
                del new
                new = pathlib.Path(f'file{i + 1}{src.suffix}')
            new.touch(mode=0o644)
            files.append(new)
    files.append(output)
    seq_count = len(files)

    if reverse:
        method = max
    else:
        method = min

    distr = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]
    empty_series = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]

    if src.suffix == ".csv":
        current_line = 1
        LIMIT_ELEMENT += 1
        with open(src.name, mode="r") as file:
            fieldnames = file.readline()
        for f in files:
            with open(f.name, mode="a") as file:
                file.write(fieldnames)
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
                for i in range(seq_count - 1):
                    empty_series[i] = distr0 + distr[i + 1] - distr[i]
                    distr[i] = distr0 + distr[i + 1]
            cfile = 0

        with open(src.name, mode="r") as file:
            row = file.readlines()[current_line]

        with open(files[cfile].name, mode="a") as file:
            file.write(row)

        empty_series[cfile] -= 1
        current_line += 1

    if set(empty_series) != {0}:
        distribution(files, empty_series)
        loops += 1
    length_of_series = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]
    del distr

    if source.suffix == ".csv":
        csv_sort(files=files, length_of_series=length_of_series, loops=loops,
                 seq_count=seq_count, key=key, output=output, method=method, fieldnames=fieldnames)


def csv_sort(files, length_of_series: list,
             loops: int, seq_count: int, key, output, method: Callable, fieldnames: str):
    iteration = 0
    list_for_merge = list()
    while loops > 0:
        iteration += 1
        data = []
        for cfile in range(seq_count - 1):
            with open(files[cfile], mode="r") as file:
                data = file.readlines()[:length_of_series[cfile] + 1]
            if not len(data)-1:
                loops -= 1
                if loops > 0:
                    files = update_map_of_files(files, cfile)
                    length_of_series = update_series(length_of_series, cfile)
                list_for_merge.clear()
                break
            csv_data = csv.DictReader(data, delimiter=';')
            list_for_merge.extend(list(csv_data))

        if not len(data)-1:
            continue

        for cfile in range(seq_count - 1):
            with open(files[cfile], mode="r") as file:
                data = file.readlines()
                data[1:length_of_series[cfile]+1] = ["" for _ in data[1:length_of_series[cfile]+1]]
                new_data = [line for line in data if line not in file.readlines()[1:length_of_series[cfile] + 1]]
            with open(files[cfile], mode="w") as file:
                file.writelines(new_data)

        real_series = [element for element in list_for_merge if list(element.values())[0] != "none"]
        empty_series = [element for element in list_for_merge if element not in real_series]
        real_series = [check_type(element) for element in real_series]
        sort_series = list()

        while real_series:
            selected = method(real_series, key=key)
            sort_series.append(selected)
            index_selected = real_series.index(selected)
            real_series.pop(index_selected)
        for element in sort_series:
            for k in element.keys():
                element[k] = str(element[k])

        if empty_series:
            sort_series.extend(empty_series)

        with open(files[-1], mode="w") as file:
            file.write(fieldnames)
            write_csv = csv.writer(file, delimiter=";")
            for row in sort_series:
                write_csv.writerow(list(row.values()))

    with open(files[-1].name, mode="r") as file:
        new_data = file.readlines()
    new_data = [line for line in new_data if "none" not in line]

    with open(output.name, mode="w") as output_file:
        output_file.writelines(new_data)

    files.remove(output)
    for file in files:
        with open(file.name, mode="w") as file:
            file.truncate(0)


def update_map_of_files(files, cfile):
    old_out = files[-1]
    new_out = files[cfile]
    files[-1] = new_out
    files[cfile] = old_out
    with open(files[-1].name, mode="w") as file:
        file.truncate(0)
    return files


def update_series(length_of_series: list, cfile: int):
    length_of_series[-1] = sum(length_of_series)
    length_of_series[cfile] = length_of_series[-1]
    length_of_series[-1] = 0

    return length_of_series


def check_type(element):
    for el in element.keys():
        has_digit = any([char.isdigit() for char in element[el]])
        has_letters = any([char.isalpha() for char in element[el]])
        if has_digit and has_letters:
            element[el] = str(element[el])
        elif has_digit and not has_letters:
            if "." in element[el]:
                element[el] = float(element[el])
            else:
                element[el] = int(element[el])
        else:
            element[el] = str(element[el])
    return element


def distribution(files: list, empty_series: list):
    resum = sum(empty_series)
    cfile = 0
    while resum > 0:
        if empty_series[cfile] < empty_series[cfile + 1]:
            cfile += 1
        else:
            cfile = 0

        files[cfile].open(mode="+a").write("none;\n")
        resum -= 1
        empty_series[cfile] -= 1


my_sort("file1.csv", key=lambda x: -x["Возраст"], output="response.csv", LIMIT_ELEMENT=50, reverse=True)
