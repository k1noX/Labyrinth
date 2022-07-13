
class GridFileException(Exception):
    def __init__(self, name: str):
        self._name = name
        
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new: str):
        self._name = new

    def __str__(self):
        return self._name


class FileFormatException(GridFileException):
    def __str__(self):
        return "Неверный формат файла!\n " + self.name


class FileNotFoundException(GridFileException):
    def __str__(self):
        return "Файл не найден!\n " + self.name
