import os

from explorer import explore
from importer import get_callables
from source_parser import Parser
from pathlib import Path


class Analyzer:
    def __init__(self, path: str) -> None:
        self.path = path
        self.directories = explore(path, ignored=[".git"])
        self.files_paths: list[Path] = self.generate_files_path()
        self.raw_map = self.__create_raw_map()
        self.calls_map_string = self.generate_calls_map_in_string()

    def generate_files_path(self):
        files = []
        for path, items in self.directories.items():
            for item in items:
                abs_path = Path(os.path.join(path, item))
                if abs_path.is_file() and abs_path.suffix == ".py":
                    files.append(abs_path)
        return files

    def generate_calls_map_in_string(self):
        calls_map_string = {}
        for path in self.files_paths:
            with open(path) as file:
                source = file.read()
            p = Parser(source)
            calls_map_string.update(p.encapsulated_callables())

        return calls_map_string

    def __create_raw_map(self) -> dict:
        """
        Create an unorganized map of an applications calls
        Returns a dictionary with this structure:
        {"object_name": <object>}
        """
        raw_map = {}
        for path in self.files_paths:
            callables = get_callables(path)
            if callables is not None:
                raw_map.update({callable.__name__: callable for callable in callables if hasattr(callable, "__name__")})
        self.raw_map = raw_map
        return raw_map

    def create_map(self, call):
        app_map = {}

        def internal_func(call, app_map, calls_map_string, raw_map):
            app_map[call] = {}
            if call.__name__ in calls_map_string.keys():
                for subcall_name in calls_map_string[call.__name__]:
                    subcall = raw_map[subcall_name]
                    app_map[call].update({subcall: {}})
                    internal_func(subcall, app_map[call], calls_map_string, raw_map)
            return app_map

        return internal_func(call, app_map, self.calls_map_string, self.raw_map)


if __name__ == "__main__":
    a = Analyzer("/home/luiz/thoughtful_repos/support/mapper/libraries/")
    print(a.raw_map)
    print(a.directories)
    print(a.files_paths)
    print(a.calls_map_string)
    from module import function

    x = a.create_map(function)
    print(x)
