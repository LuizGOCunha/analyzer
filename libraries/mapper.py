import os
import sys
import ast

from explorer import explore
from source_parser import Parser
from pathlib import Path

from models.class_def import ClassMd


class Analyzer:
    def __init__(self, path: str) -> None:
        self.path = path
        self.directories = explore(path, ignored=[".git", "venv", "__pycache__"])
        self.files_paths: list[Path] = self.__generate_files_path()
        self.raw_map = self.__generate_raw_map()

    def identify_max_browser_bug(self):
        """
        Looks for a bug belonging to this pattern of code:

        b.set_window_size(1920, 1600)
        b.maximize_browser_window()
        """
        culprit_list = []
        for model_object in self.raw_map.values():
            tree_iterator = ast.iter_child_nodes(model_object.source)
            for node in tree_iterator:
                is_cold_method_call = (
                    isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                )
                attr_is = lambda attr: node.value.func.attr == attr

                if is_cold_method_call and attr_is("set_window_size"):
                    node = tree_iterator.__next__()
                    if is_cold_method_call and attr_is("maximize_browser_window"):
                        culprit_list.append((model_object.location, node.lineno))
        return culprit_list

    def __generate_raw_map(self):
        """
        Generate a mapping of {definition_name: definition_model}
        """
        raw_map = {}
        for path in self.files_paths:
            p = Parser(path)
            raw_map.update({funcmd.name: funcmd for funcmd in p.functions})
            for classmd in p.classes:
                raw_map[classmd.name] = classmd
                raw_map.update({methodmd.name: methodmd for methodmd in classmd.methods})
        return raw_map

    def __generate_files_path(self):
        files = []
        for path, items in self.directories.items():
            for item in items:
                abs_path = Path(os.path.join(path, item))
                if abs_path.is_file() and abs_path.suffix == ".py":
                    files.append(abs_path)
        return files

    def __adjust_classmd_call(self, call):
        """
        Checks if the call is a Class, is so returns it's initiation
        else returns the same call
        """
        if isinstance(call, ClassMd):
            for method in call.methods:
                if method.name == "__init__":
                    return method
            # If it's a class, but doesn't have a init method, simply skip
            return None
        else:
            return call

    # TODO: A way to gather code inside of blocks (for, try, if, etc)
    def create_calls_map(self, call_name):
        """
        Creates map of function objects based on information from Analyzer.
        Receives call from inside the Analyzed directory.
        Returns a dictionary with this structure:
        {<FunctionMd function>: {<FunctionMd call1>: {<ClassMd 'Cls'>: {}}, <ClassMd call2>: {}}}
        """
        app_map = {}
        if call_name not in self.raw_map.keys():
            raise IndexError("call name not present in raw map")
        else:
            call = self.raw_map[call_name]

        def internal_func(self: Analyzer, call, app_map: dict):
            app_map[call] = {}
            call = self.__adjust_classmd_call(call)
            if call is None:
                return app_map
            for subcall_name in call.calls:
                if subcall_name not in self.raw_map.keys():
                    continue
                else:
                    subcall = self.raw_map[subcall_name]
                    subcall = self.__adjust_classmd_call(subcall)
                    if subcall is None:
                        continue
                app_map[call].update({subcall: {}})
                internal_func(self, subcall, app_map[call])
            return app_map

        return internal_func(self, call, app_map)


if __name__ == "__main__":
    a = Analyzer("/home/luiz/thoughtful_repos/support/mapper/libraries/")
    # a = Analyzer("/home/luiz/thoughtful_repos/sb1-training-management/")
    print(">> DIRECTORIES:")
    print(a.directories)
    print(">> FILE PATHS:")
    print(a.files_paths)
    print(">> RAW MAP")
    print(a.raw_map)
    culprit = a.identify_max_browser_bug()
    if culprit:
        print(">> BROWSER MAX CULPRIT")
        print(culprit)
        breakpoint()
    print(">> CALL MAP")
    from pprint import pformat

    x = pformat(x := a.create_calls_map("task"))
    print(x)
    with open("file.txt", "w") as file:
        file.write(x)

    # x = a.create_object_map(function)
    # print(x)
