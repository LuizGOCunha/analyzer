import ast
import os
from pathlib import Path

from libraries.diagram_maker import Diagram
from libraries.explorer import explore
from libraries.models.class_def import ClassMd, MethodMd
from libraries.models.function_def import FunctionMd
from libraries.models.unknown_func import UnknownFuncMd
from libraries.source_parser import Parser


class Analyzer:
    def __init__(self, path: str) -> None:
        self.path = path
        self.directories = explore(path, ignored=[".git", "venv", "__pycache__"])
        self.files_paths: list[Path] = self.__generate_files_path()
        self.raw_map, self.models_list = self.__gather_call_models()

    def identify_max_browser_bug(self):
        """
        Looks for a bug belonging to this pattern of code:

        b.set_window_size(1920, 1600)
        b.maximize_browser_window()
        """
        culprit_list = []
        for model_object in self.models_list:
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

    def __gather_call_models(self) -> tuple[dict, list]:
        """
        Generate a tuple containing raw map of models and list of all models.
        raw_map: A dictionary where key is the calls name, a model or list of models with that name
        models_list: Linear list of all gathered models
        """
        raw_map = {}
        models_list = []
        for path in self.files_paths:
            p = Parser(path)
            for funcmd in p.functions:
                models_list.append(funcmd)
                raw_map = self.__add_models_to_raw_map(funcmd, raw_map)
            for classmd in p.classes:
                models_list.append(classmd)
                raw_map = self.__add_models_to_raw_map(classmd, raw_map)
                for methodmd in classmd.methods:
                    models_list.append(methodmd)
                    raw_map = self.__add_models_to_raw_map(methodmd, raw_map)
        return raw_map, models_list

    def __add_models_to_raw_map(self, model: FunctionMd | ClassMd | MethodMd | UnknownFuncMd, raw_map: dict) -> dict:
        """
        Add models to a raw_map, with all the necessary checks that it implies
        """
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

    def __handle_list_of_models(self, model_list: list[FunctionMd]):
        """
        Centralization of the way to handle list of models inside the raw_map
        """
        for model in model_list:
            if model.location.name == "task.py":
                return model
        return model_list[0]

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
            return self.__handle_list_of_models(call)
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
                call = self.__handle_list_of_models(call)

        def internal_func(self: Analyzer, call, app_map: dict):
            nonlocal calls_used
            calls_used.append(call)
            call = self.__adjust_call(call)
            if call not in app_map.keys():
                app_map[call] = {}
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
                # Removed when realized it's unnecessary logic, will do some auditing before deleting completely
                # app_map[call].update({subcall: {}})
                internal_func(self, subcall, app_map[call])
            return app_map

        return internal_func(self, call, app_map)

    def create_diagram(self, call_name: str, show_unknown: bool = False, path: str | Path | None = None):
        """
        Creates the code for a mermaid diagram that maps the calls inside a repository
        Only needs the call name that should be mapped
        Args:
        - call_name(str): name of the call that you want to map
        - show_unknowns(bool): sets if calls of unknown source should be tracked
        - path(str | Path | None): path for thecreation of the diagram file, if not given, returns the diagram as string
        """
        cmap = self.create_calls_map(call_name, show_unknown)
        diagram = Diagram(map=cmap, diagram_title=f"{call_name} workflow")
        if path is None:
            return diagram.diagram_code
        else:
            return diagram.create_diagram_file(path)


if __name__ == "__main__":
    # a = Analyzer("/home/luiz/thoughtful_repos/support/mapper/libraries/")
    a = Analyzer("/home/luiz/thoughtful_repos/verisk3-data-entry/")
    # print(">> DIRECTORIES:")
    # print(a.directories)
    # print(">> FILE PATHS:")
    # print(a.files_paths)
    # print(">> RAW MAP")
    # print(a.raw_map)
    # for call in a.raw_map.values():
    #     print(call)
    # culprit = a.identify_max_browser_bug()
    # if culprit:
    #     print(">> BROWSER MAX CULPRIT")
    #     print(culprit)
    print(">> CALL MAP")
    from pprint import pprint

    cmap = a.create_calls_map("task")
    pprint(cmap)

    diagram = Diagram(cmap)
    diagram.create_diagram_file("diagram.txt")

    # x = a.create_object_map(function)
    # print(x)
