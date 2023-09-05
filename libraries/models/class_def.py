from __future__ import annotations
import ast
from models.exceptions import NonMethodError
from models.function_def import FunctionMd


class MethodMd(FunctionMd):
    def __init__(self, source: FunctionMd, class_object: ClassMd) -> None:
        super().__init__(source)
        self.class_object = class_object
        self.attributes = self.__get_attributes()
        try:
            self.self_name = self.arguments[0]
        except IndexError:
            raise NonMethodError("Passed function doesn't have a first arg, make sure this is a Method definition")

    def __get_attributes(self):
        attributes = []
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.Assign):
                attributes.extend([target.attr for target in node.targets if isinstance(target, ast.Attribute)])
        return list(set(attributes))

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.class_object.name}.{self.name}>"


class ClassMd(FunctionMd):
    def __init__(self, source: ast.ClassDef) -> None:
        super().__init__(source)
        self.methods = [MethodMd(item, self) for item in self.body if isinstance(item, ast.FunctionDef)]
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
