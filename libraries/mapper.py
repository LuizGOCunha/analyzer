import ast
import os
import sys
from pathlib import Path

from diagram_maker import diagram_maker
from explorer import explore
from models.class_def import ClassMd, MethodMd
from models.function_def import FunctionMd
from models.unknown_func import UnknownFuncMd
from python_mermaid.diagram import MermaidDiagram
from source_parser import Parser


class Analyzer:
    def __init__(self, path: str) -> None:
        self.path = path
        self.directories = explore(path, ignored=[".git", "venv", "__pycache__"])
        self.files_paths: list[Path] = self.__generate_files_path()
        self.raw_map = self.__generate_raw_map()
        # TODO: add calls_list for iterating all models

    def identify_max_browser_bug(self):
        """
        Looks for a bug belonging to this pattern of code:

        b.set_window_size(1920, 1600)
        b.maximize_browser_window()
        """
        culprit_list = []
        all_models = []
        for value in self.raw_map.values():
            if isinstance(value, list):
                [all_models.append(model) for model in value]
            else:
                all_models.append(value)
        for model_object in all_models:
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
            for funcmd in p.functions:
                raw_map = self.__add_models_to_raw_map(funcmd, raw_map)
            for classmd in p.classes:
                raw_map = self.__add_models_to_raw_map(classmd, raw_map)
                for methodmd in classmd.methods:
                    raw_map = self.__add_models_to_raw_map(methodmd, raw_map)
        return raw_map

    def __add_models_to_raw_map(self, model: FunctionMd | ClassMd | MethodMd | UnknownFuncMd, raw_map: dict) -> dict:
        """
        Add models to a raw_map, with all the necessary checks that it implies
        """
        # There's no point in adding generic methods like dunders, since they will repeat in most classes
        if model.name[-2:] == "__" and model.name[:2] == "__":
            return raw_map
        # This handles calls with same name that aren't the same object, creating a list with objects or adding to it
        if model.name in raw_map.keys():
            if model is not raw_map[model.name]:
                if isinstance(raw_map[model.name], list):
                    raw_map[model.name].append(model)
                    raw_map[model.name] = list(set(raw_map[model.name]))
                    return raw_map
                else:
                    raw_map[model.name] = [raw_map[model.name], model]
                    return raw_map
                pass
        raw_map[model.name] = model
        return raw_map

    def __generate_files_path(self):
        files = []
        for path, items in self.directories.items():
            for item in items:
                abs_path = Path(os.path.join(path, item))
                if abs_path.is_file() and abs_path.suffix == ".py":
                    files.append(abs_path)
        return files

    def __adjust_call(self, call: FunctionMd | ClassMd | MethodMd | UnknownFuncMd | list):
        """
        Adjusts the call gathered from the raw_map, doing all necessary checks
        If no adjustments are necessary, returns the same call
        """
        if isinstance(call, ClassMd):
            for method in call.methods:
                if method.name == "__init__":
                    return method
            # If it's a class, but doesn't have a init method, simply skip
            return None
        if isinstance(call, list):
            # TODO: do some handling to get the ideal call. As a placeholder we're returning the first one
            return call[0]
        else:
            return call

    def create_calls_map(self, call_name: str, show_unknowns: bool = False) -> dict:
        """
        Creates map of function objects based on information from Analyzer.
        Receives call from inside the Analyzed directory.
        Args:
        - call_name(str): name of the call that you want to map
        - show_unknowns(bool): sets if calls of unknown source should be tracked

        Returns a dictionary with this structure:
        {<FunctionMd function>: {<FunctionMd call1>: {<ClassMd 'Cls'>: {}}, <ClassMd call2>: {}}}
        """
        app_map = {}
        calls_used = []
        if call_name not in self.raw_map.keys():
            raise IndexError("call name not present in raw map")
        else:
            call = self.raw_map[call_name]
            if isinstance(call, list):
                call = call[0]

        def internal_func(self: Analyzer, call, app_map: dict):
            nonlocal calls_used
            calls_used.append(call)
            app_map[call] = {}
            call = self.__adjust_call(call)
            if call is None:
                return app_map
            for subcall_name in call.calls:
                if subcall_name not in self.raw_map.keys():
                    if show_unknowns:
                        subcall = UnknownFuncMd(subcall_name)
                    else:
                        continue
                else:
                    subcall = self.raw_map[subcall_name]
                    subcall = self.__adjust_call(subcall)
                    if subcall is None or subcall in calls_used[:-3]:
                        continue
                app_map[call].update({subcall: {}})
                internal_func(self, subcall, app_map[call])
            return app_map

        return internal_func(self, call, app_map)


if __name__ == "__main__":
    # a = Analyzer("/home/luiz/thoughtful_repos/support/mapper/libraries/")
    a = Analyzer("/home/luiz/thoughtful_repos/sb1-training-management/")
    # print(">> DIRECTORIES:")
    # print(a.directories)
    # print(">> FILE PATHS:")
    # print(a.files_paths)
    # print(">> RAW MAP")
    # print(a.raw_map)
    # for call in a.raw_map.values():
    #     print(call)
    culprit = a.identify_max_browser_bug()
    # breakpoint()
    if culprit:
        print(">> BROWSER MAX CULPRIT")
        print(culprit)
    print(">> CALL MAP")
    from pprint import pprint

    cmap = a.create_calls_map("red_cross_workflow")
    # pprint(cmap)

    nodes, links = diagram_maker(cmap)
    diagram = MermaidDiagram("diagram", nodes, links)
    with open("/home/luiz/thoughtful_repos/support/mapper/diagram.txt", "w") as file:
        diagram_str = diagram.__str__()
        file.write(diagram_str)

    # x = a.create_object_map(function)
    # print(x)
