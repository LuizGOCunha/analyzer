from astunparse import unparse
from pathlib import Path
from typing import Union
import ast
import re


class FunctionMd:
    def __init__(self, source: ast.FunctionDef, location: Union[str, Path, None] = None) -> None:
        self.source = source
        self.name = self.source.name
        self.body = self.source.body
        if isinstance(location, str):
            location = Path(location)
        self.location = location
        self.tree = ast.parse(source)
        self.arguments = self.__get_arguments()
        self.docstring = self.__get_docstring()
        self.vars = self.__get_variables()
        self.calls = self.__get_calls()

    def __get_calls(self, tree=None):
        if tree is None:
            tree = self.tree
        calls = []

        for node in ast.iter_child_nodes(tree):
            # cold calls cases / Ex:call()
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                # Methods
                if isinstance(node.value.func, ast.Attribute):
                    calls.append(node.value.func.attr)
                # Functions
                elif isinstance(node.value.func, ast.Name):
                    calls.append(node.value.func.id)
            # assignment call cases / Ex: var = call()
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                # Methods
                if isinstance(node.value.func, ast.Attribute):
                    calls.append(node.value.func.attr)
                # Functions
                elif isinstance(node.value.func, ast.Name):
                    calls.append(node.value.func.id)
            # blocks of code that need to be stepped into
            elif isinstance(node, (ast.For, ast.Try, ast.If, ast.While)):
                calls.extend(self.__get_calls(tree=node))
        return calls

    def __get_docstring(self):
        first_item = self.source.body[0]
        if isinstance(first_item, ast.Expr) and isinstance(first_item.value, ast.Str):
            return re.sub(r"(\n|\\n)", "", unparse(first_item))
        return None

    def __get_arguments(self):
        first_iter_item = ast.iter_child_nodes(self.tree).__next__()
        if isinstance(first_iter_item, ast.arguments):
            ast_args = first_iter_item.args
            return [ast_arg.arg for ast_arg in ast_args]
        else:
            return None

    def __get_variables(self):
        variables = []
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.Assign):
                variables.extend([target.id for target in node.targets if isinstance(target, ast.Name)])
        return variables

    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.name}>"


if __name__ == "__main__":
    with open("/home/luiz/thoughtful_repos/support/mapper/libraries/module.py") as file:
        tree = ast.parse(file.read())
        for node in ast.iter_child_nodes(tree):
            if type(node) == ast.FunctionDef and node.name == "call1":
                fd = FunctionMd(node)
                breakpoint()
                # print(fd.name, fd.arguments, fd.body, fd.calls, fd.docstring, fd.vars)
