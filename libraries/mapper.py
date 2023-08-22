import os

from explorer import explore
from importer import get_callables
from source_parser import Parser


class Analyzer:
    def __init__(self, path: str) -> None:
        self.path = path
        self.directories = explore(path, ignored=[".git"])
        self.raw_map = self.__create_raw_map()

    def __create_raw_map(self) -> dict:
        """
        Create an unorganized map of an applications calls
        Returns a dictionary with this structure:
        {"object_name": <object>}
        """
        raw_map = {}
        for path, items in self.directories.items():
            for item in items:
                abs_path = os.path.join(path, item)
                callables = get_callables(abs_path)
                if callables is not None:
                    raw_map.update(
                        {callable.__name__: callable for callable in callables if hasattr(callable, "__name__")}
                    )
        self.raw_map = raw_map
        return raw_map

    def create_map(self):
        pass


if __name__ == "__main__":
    a = Analyzer("/home/luiz/thoughtful_repos/support/mapper/libraries/")
    print(a.raw_map)
