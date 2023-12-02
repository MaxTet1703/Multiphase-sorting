import csv
import pathlib
import string
from random import random, choice
from typing import Callable, Optional

CURRENT_PATH = pathlib.Path().cwd()


def my_sort(src, output=None, reverse: bool = False,
            key=None, LIMIT_ELEMENT=40, seq=3) -> None:
    """
    Создание последовательностей, работа с параметрами scr и output,
    Распределение элементов в последовательности
    :param src: Входной файл, может быть несколько
    :param output: Выходной файл
    :param reverse: Флаг обратной сортировки
    :param key: Ключ сортировки
    :param LIMIT_ELEMENT: Число сортируемых элементов
    :param seq: Число последовтельностей
    :return:
    """
    link = None
    if isinstance(src, list):
        if len(src) == 1:
            src = src[0]
            src = CURRENT_PATH / src
        else:

            for i in range(len(src)):
                src[i] = CURRENT_PATH / src[i]
                if not src[i].exists:
                    src.remove(src[i])
            if not src:
                raise FileExistsError

            link = CURRENT_PATH / f"link{src[0].suffix}"
            if not link.exists():
                link.touch(mode=0o644)
            else:
                with open(link, mode="+a") as file:
                    file.truncate(0)

            if src[0].suffix == ".csv":
                with open(link, mode="w") as link_file, open(src[0], mode="r") as file:
                    link_file.write(file.readlines()[0])

            for i in range(len(src)):
                with open(src[i], mode="r") as read_file, open(link, mode="a") as write_file:
                    if src[i].suffix == ".csv":
                        write_file.writelines(read_file.readlines()[1::])
                        write_file.write("\n")
                    else:
                        write_file.writelines(read_file.readlines())
            src = link
    else:
        src = CURRENT_PATH / src
        if not src.exists():
            raise FileExistsError("File is not exist in the directory")
    if not output:
        output = pathlib.Path(CURRENT_PATH / f"response{src.suffix}")
        if not output.exists():
            output.touch(mode=0o644)
        else:
            with open(output.name, mode="w") as file:
                file.truncate()
    else:
        output = CURRENT_PATH / output
        if output.exists():
            with open(output.name, mode="w") as file:
                file.truncate()
        else:
            output.touch(mode=0o644)

    files = list()
    letters = string.ascii_letters

    for _ in range(seq):
        file = "".join(choice(letters) for i in range(5)) + f"{src.suffix}"
        file = CURRENT_PATH / file
        if not file.exists():
            file.touch(mode=0o644)
        files.append(file)
    del letters
    files.append(output)
    seq_count = len(files)

    if reverse:
        method = max
    else:
        method = min
    src_file = open(src.name, mode="r")
    distr = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]
    empty_series = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]
    if src.suffix == ".csv":
        current_line = 1
        fieldnames = src_file.readline()
        for f in files:
            file = open(f.name, mode="w")
            file.write(fieldnames)
            file.close()
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

        row = src_file.readline().replace("\n", "")
        if not row:
            break
        file = open(files[cfile].name, mode="a")
        file.write(row + "\n")
        file.close()
        empty_series[cfile] -= 1
        current_line += 1
    src_file.close()

    if sum(empty_series) != 0:
        distribution(files, empty_series)
    loops += 1

    length_of_series = [0 if i == seq_count - 1 else 1 for i in range(seq_count)]
    del distr

    if link is not None:
        link.unlink()
    if src.suffix == ".csv":
        csv_sort(files=files, length_of_series=length_of_series, loops=loops,
                 seq_count=seq_count, key=key, output=output, method=method, fieldnames=fieldnames)
    else:

        txt_sort(files=files, length_of_series=length_of_series,
                 loops=loops, seq_count=seq_count, method=method, output=output)


def txt_sort(files, length_of_series: list,
             loops: int, seq_count: int, output, method: Callable):
    """
    Многофазная сортировка для .txt файлов
    :param files: пути к последовтаельностям и выходному файлу
    :param length_of_series: длина серий в каждом файле
    :param loops: Число прохожов
    :param seq_count: Число последовательностей
    :param output: Выходной файл
    :param method: Метод сопоставимый с reverse
    :return:
    """
    list_for_merge = list()
    while loops > 0:
        data = []
        for cfile in range(seq_count - 1):
            with open(files[cfile].name, mode="r") as file:
                data = file.readlines()[:length_of_series[cfile]]
            if not len(data):
                loops -= 1
                if loops > 0:
                    files = update_map_of_files(files, cfile)
                    length_of_series = update_series(length_of_series, cfile)
                list_for_merge.clear()
                break
            data = [el.replace("\n", "") for el in data]
            list_for_merge.extend(data)

        if not len(data):
            continue

        for cfile in range(seq_count - 1):
            with open(files[cfile].name, mode="r") as file:
                data = file.readlines()
                data[:length_of_series[cfile]] = ["" for _ in data[:length_of_series[cfile]]]
                new_data = [line for line in data if line not in file.readlines()[:length_of_series[cfile]]]
            with open(files[cfile].name, mode="w") as file:
                file.writelines(new_data)

        real_series = [element for element in list_for_merge if "none" not in element]
        empty_series = [element for element in list_for_merge if element not in real_series]
        real_series = [check_type_txt(element) for element in real_series]
        sort_series = list()

        while real_series:
            selected = method(real_series)
            sort_series.append(selected)
            index_selected = real_series.index(selected)
            real_series.pop(index_selected)
        for i in range(len(sort_series)):
            sort_series[i] = str(sort_series[i])

        if empty_series:
            sort_series.extend(empty_series)

        with open(files[-1].name, mode="a") as file:
            for row in sort_series:
                file.write(row + "\n")
        list_for_merge.clear()
        sort_series.clear()
    if files[0] != output:
        with open(files[0].name, mode="r") as file, open(output.name, mode="w") as output_file:
            output_file.writelines([line for line in file.readlines() if "none" not in line])
    else:
        with open(output.name, mode="r+") as file:
            file.seek(0)
            for line in file.readlines():
                if "none" not in line:
                    with open(files[-1].name, mode="a") as out:
                        out.write(line)
        with open(files[-1].name, mode="r") as file, open(output.name, mode="w") as output_file:
            output_file.writelines(file.readlines())
    files.remove(output)
    for file in files:
        file.unlink()


def csv_sort(files, length_of_series: list,
             loops: int, seq_count: int, key, output, method: Callable, fieldnames: str):
    """
    Многофазная сортировка для .csv файлов
    :param files: пути к последовтаельностям и выходному файлу
    :param length_of_series: длина серий в каждом файле
    :param loops: Число прохожов
    :param seq_count: Число последовательностей
    :param output: Выходной файл
    :param method: Метод сопоставимый с reverse
    :param fieldnames: Поля таблицы
    :return:
    """
    print(loops)
    list_for_merge = list()
    while loops > 0:
        data = []
        for cfile in range(seq_count - 1):
            with open(files[cfile].name, mode="r") as file:
                data = file.readlines()[:length_of_series[cfile] + 1]
            if not len(data) - 1:
                loops -= 1
                if loops > 0:
                    files = update_map_of_files(files, cfile, fieldnames)
                    length_of_series = update_series(length_of_series, cfile)
                list_for_merge.clear()
                break
            csv_data = csv.DictReader(data, delimiter=';')
            list_for_merge.extend(list(csv_data))

        if not len(data) - 1:
            continue

        for cfile in range(seq_count - 1):
            with open(files[cfile].name, mode="r") as file:
                data = file.readlines()
                data[1:length_of_series[cfile] + 1] = ["" for _ in data[1:length_of_series[cfile] + 1]]
                new_data = [line for line in data if line not in file.readlines()[1:length_of_series[cfile] + 1]]
            with open(files[cfile].name, mode="w") as file:
                file.writelines(new_data)

        real_series = [element for element in list_for_merge if list(element.values())[0] != "none"]
        empty_series = [element for element in list_for_merge if element not in real_series]
        real_series = [check_type_csv(element) for element in real_series]
        sort_series = list()

        while real_series:
            selected = method(real_series, key=lambda x: x[key])
            sort_series.append(selected)
            index_selected = real_series.index(selected)
            real_series.pop(index_selected)
        for element in sort_series:
            for k in element.keys():
                element[k] = str(element[k])

        if empty_series:
            sort_series.extend(empty_series)

        with open(files[-1].name, mode="a") as file:
            write_csv = csv.writer(file, delimiter=";")
            for row in sort_series:
                write_csv.writerow(list(row.values()))
        list_for_merge.clear()
        sort_series.clear()

    if files[0] != output:
        with open(files[0].name, mode="r") as file, open(output.name, mode="w") as output_file:
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
        file.unlink()


def update_map_of_files(files, cfile, fieldnames=None):
    """
    Переопределение карты индексов в files после окончания прохода
    :param files: Список путей к файлам
    :param cfile: Индекс файла, который станет выходным
    :param fieldnames: Поля таблицы
    :return: Обновленный files
    """
    old_out = files[-1]
    new_out = files[cfile]
    files[-1] = new_out
    files[cfile] = old_out
    with open(files[-1].name, mode="w") as file:
        file.truncate(0)
        if fieldnames is not None:
            file.write(fieldnames)
    return files


def update_series(length_of_series: list, cfile: int):
    """
    Обновление числа серий в файлах
    :param length_of_series: Список длин серий
    :param cfile: Индекс файла, который станет входным
    :return: обновленный lenght_of_series
    """
    length_of_series[-1] = sum(length_of_series)
    length_of_series[cfile] = length_of_series[-1]
    length_of_series[-1] = 0

    return length_of_series


def check_type_csv(element):
    """
    Преобразования элемента в нужный тип данных для сравнения в csv
    :param element: Сам элемент
    :return: преобразованный элемент
    """
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


def check_type_txt(element):
    """
     Преобразования элемента в нужный тип данных для сравнения в csv
    :param element: Сам элемент
    :return: преобразованный элемент
    """
    has_digit = any([char.isdigit() for char in element])
    has_letters = any([char.isalpha() for char in element])
    if has_digit and has_letters:
        element = str(element)
    elif has_digit and not has_letters:
        if "." in element:
            element = float(element)
        else:
            element = int(element)
    else:
        element = str(element)

    return element


def distribution(files: list, empty_series: list):
    """
    Дополнения пос-тей пустыми сериями, если рапсределение неравномерное
    :param files: список файлов
    :param empty_series: Список кол-ва пустых серий в каждом файле
    :return:
    """
    for cfile in range(len(files) - 1):
        if empty_series[cfile] != 0:
            with open(files[cfile].name, mode="a") as file:
                for _ in range(empty_series[cfile]):
                    file.write("none;\n")


