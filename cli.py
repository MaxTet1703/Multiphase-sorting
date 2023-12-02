import argparse

from my_sort import my_sort


def parser():
    """
    CLI для сортировки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, nargs="+", help="Входной(ые) файл(ы)")
    parser.add_argument("-o", "--output", type=str, help="Выходной файл")
    parser.add_argument("-k", "--key", type=str, help="Ключ сортировки")
    parser.add_argument("-r", "--reverse", action=argparse.BooleanOptionalAction, help="Флаг обратной сортировки")
    parser.add_argument("-l", "--limit", type=int, help="Число элементов из входного файла")
    parser.add_argument("-sq", "--sequence", type=int, help="Число файлов, участвующих в сортировке")

    pars = parser.parse_args()
    if not pars.sequence:
        pars.sequence = 3
    if not pars.limit:
        pars.limit = 40

    my_sort(src=pars.source,
            output=pars.output,
            key=pars.key,
            reverse=pars.reverse,
            LIMIT_ELEMENT=pars.limit,
            seq=pars.sequence
            )


if __name__ == "__main__":
    parser()
