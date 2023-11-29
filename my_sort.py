import csv
import pathlib
from typing import Callable, Optional
from pydantic.types import PathType

CURRENT_PATH = pathlib.Path().cwd()
source = CURRENT_PATH / "file1.csv"
error = CURRENT_PATH / "sdfsdfsf.txt"


def my_sort(src: PathType, output: Optional[PathType] = None, reverse: bool = False,
            key: Optional[Callable] = None, LIMIT_ELEMENT = 40) -> None:
    src_list = []
    link = None
    if isinstance(src, list):
        if len(src) == 1:
            src = src[0]
        else:

            link = CURRENT_PATH / "link.csv"
            if not link.exists():
                link.touch(mode=0o644)
            else:
                with open(link, mode="w") as file:
                    file.truncate(0)

            for i in range(len(src)):
                src[i] = CURRENT_PATH / src[i]
                if not src[i].exists:
                    src.remove(src[i])
            if not src:
                raise FileExistsError

            if src[0].suffix == ".csv":
                with open(link, mode="w") as link_file, open(src[0], mode="r") as file:
                    link_file.write(file.readlines()[0])

            for i in range(len(src)):
                with open(src[i], mode="r") as read_file, open(link, mode="a") as write_file:
                    if src[i].suffix == ".csv":
                        write_file.writelines(read_file.readlines()[1::])
                        write_file.write("\n")
                    else:
                        write_file.write(read_file.readlines())
            src_list = src
            src = link
    else:
        src = CURRENT_PATH / src
        if not src.exists():
            raise FileExistsError("File is not exist in the directory")

    if output is None:
        output = pathlib.Path(CURRENT_PATH / f"response{source.suffix}")
        output.touch(mode=0o644)
    else:
        output = CURRENT_PATH / output
        if output.exists():
            with open(output, mode="w") as file:
                file.truncate()
        else:
            output.touch(mode=0o644)

    files = [file for file in CURRENT_PATH.glob(f'*{src.suffix}') if file not in src_list and file != src and file != output]

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
    loops = 1

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
            row = file.readlines()[current_line:current_line+1]
            row = ''.join(row)
        with open(files[cfile].name, mode="a") as file:
            file.write(row)

        empty_series[cfile] -= 1
        current_line += 1

    if set(empty_series) != {0}:
        distribution(files, empty_series)
        loops += 1

    length_of_series = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]
    del distr

    if link is not None:
        link.unlink()
    if source.suffix == ".csv":
        csv_sort(files=files, length_of_series=length_of_series, loops=loops,
                 seq_count=seq_count, key=key, output=output, method=method, fieldnames=fieldnames)


def csv_sort(files, length_of_series: list,
             loops: int, seq_count: int, key, output, method: Callable, fieldnames: str):
    print(loops)
    list_for_merge = list()
    while loops > 0:
        data = []
        for cfile in range(seq_count - 1):
            with open(files[cfile], mode="r") as file:
                data = file.readlines()[:length_of_series[cfile] + 1]
            if not len(data)-1:
                loops -= 1
                if loops > 0:
                    files = update_map_of_files(files, cfile, fieldnames)
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
                data[1:length_of_series[cfile] + 1] = ["" for _ in data[1:length_of_series[cfile] + 1]]
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

        with open(files[-1], mode="a") as file:
            write_csv = csv.writer(file, delimiter=";")
            for row in sort_series:
                write_csv.writerow(list(row.values()))
        list_for_merge.clear()
        sort_series.clear()

    if files[0] != output:
        with open(files[0].name, mode="r") as file, open(output.name, mode="w") as output_file :
            output_file.writelines([line for line in file.readlines() if "none" not in line])
    else:
        with open(output.name, mode="r+") as file:
            file.seek(0)
            for line in file.readlines()[1::]:
                if "none" not in line:
                    with open(files[-1].name, mode="a") as out:
                        out.write(line)
        with open(files[-1].name, mode="r") as file, open(output.name, mode="w") as output_file:
            output_file.writelines(file.readlines())
    files.remove(output)
    for file in files:
        with open(file.name, mode="w") as file:
            file.truncate(0)


def update_map_of_files(files, cfile, fieldnames):
    old_out = files[-1]
    new_out = files[cfile]
    files[-1] = new_out
    files[cfile] = old_out
    with open(files[-1].name, mode="w") as file:
        file.truncate(0)
        file.write(fieldnames)
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
    for cfile in range(len(files) - 1):
        if empty_series[cfile] != 0:
            with open(files[cfile], mode="a") as file:
                for _ in range(empty_series[cfile]):
                    file.write("none;\n")


my_sort(src="file1.csv", key=lambda x: -len(x["Имя"]), output="response.csv", LIMIT_ELEMENT=15, reverse=True)
