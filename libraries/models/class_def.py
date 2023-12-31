from __future__ import annotations

import ast

from libraries.models.exceptions import NonMethodError
from libraries.models.function_def import FunctionMd


class MethodMd(FunctionMd):
    def __init__(self, source: FunctionMd, class_object: ClassMd, location=None) -> None:
        super().__init__(source, location)
        self.class_object = class_object
        self.attributes = self.__get_attributes()
        while "__init__" in self.calls:
            calls_before = self.calls
            self.__check_for_super_init()
            calls_after = self.calls
            if calls_before == calls_after:
                break
        if self.__is_static_method():
            self.self_name = None
        else:
            try:
                self.self_name = self.arguments[0]
            except IndexError:
                raise NonMethodError("Passed function doesn't have a first arg, make sure this is a Method definition")

    def __is_static_method(self):
        for decorator in self.source.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "staticmethod":
                return True
        return False

    def __check_for_super_init(self):
        """
        Checks for the existance of super().__init__() calls
        Make sure to only call this function if an "__init__" value is present among captured calls
        """
        for node in ast.iter_child_nodes(self.source):
            # calls_init = isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "__init__"
            # calls_super = isinstance(node.value.func.value, ast.Call) and isinstance(node.value.func.value.func, ast.Name) and node.value.func.value.func.id == "super"
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "__init__"
                and isinstance(node.value.func.value, ast.Call)
                and isinstance(node.value.func.value.func, ast.Name)
                and node.value.func.value.func.id == "super"
            ):
                correct_place = self.calls.index("__init__")
                parent_class = self.class_object.parents[0]
                self.calls.remove("__init__")
                self.calls.insert(correct_place, parent_class)

    def __get_attributes(self):
        attributes = []
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.Assign):
                attributes.extend([target.attr for target in node.targets if isinstance(target, ast.Attribute)])
        return list(set(attributes))

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.class_object.name}.{self.name}>"


class ClassMd(FunctionMd):
    def __init__(self, source: ast.ClassDef, location=None) -> None:
        super().__init__(source, location)
        self.parents = [parent.id for parent in self.source.bases]
        self.methods = [MethodMd(item, self, location) for item in self.body if isinstance(item, ast.FunctionDef)]
        self.calls.extend(self.__get_method_calls())
        self.attributes = self.__get_attributes()

    def __get_attributes(self):
        attributes = self.vars
        for method in self.methods:
            attributes.extend([attribute for attribute in method.attributes])
        return list(set(attributes))

    def __get_method_calls(self):
        method_calls = []
        for method in self.methods:
            method_calls.extend([call for call in method.calls])
        return method_calls


if __name__ == "__main__":
    with open("/home/luiz/thoughtful_repos/support/mapper/libraries/module.py") as file:
        tree = ast.parse(file.read())
        for node in ast.iter_child_nodes(tree):
            if type(node) == ast.ClassDef:
                cd = ClassMd(node)
                breakpoint()
