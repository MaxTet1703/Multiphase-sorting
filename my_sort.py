import pathlib


def get_name_files():
    """
    Функция, которая записывает в два списка наименования файлов с расширениями .csv и .txt
    :return: Словарь с двумя списками, хранящие наименования файлов с соответсвующими расширениями
    """
    csv_files = []
    txt_files = []
    current_path = pathlib.Path().absolute()
    for files in current_path.iterdir():
        if files.name.endswith(".csv"):
            csv_files.append(files.name)
        elif files.name.endswith(".txt"):
            txt_files.append(files.name)
    return {
        'txt': txt_files,
        'csv': csv_files
    }
