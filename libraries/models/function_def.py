from astunparse import unparse
import ast
import re


class FunctionDef:
    def __init__(self, source: ast.FunctionDef) -> None:
        self.source = source
        self.name = self.source.name
        self.tree = ast.parse(source)
        self.arguments = self.__get_arguments()
        self.docstring = self.__get_docstring()
        self.vars = self.__get_variables()
        self.calls = self.__get_calls()
        self.body = self.source.body

    def __get_calls(self):
        calls = []
        for node in ast.iter_child_nodes(self.tree):
            # cold calls cases / Ex:call()
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                # Functions
                if isinstance(node.value.func, ast.Attribute):
                    calls.append(node.value.func.attr)
                # Methods
                elif isinstance(node.value.func, ast.Name):
                    calls.append(node.value.func.id)
            # assignment call cases / Ex: var = call()
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                # Functions
                if isinstance(node.value.func, ast.Attribute):
                    calls.append(node.value.func.attr)
                # Methods
                elif isinstance(node.value.func, ast.Name):
                    calls.append(node.value.func.id)
        return calls

    def __get_docstring(self):
        first_item = self.source.body[0]
        if isinstance(first_item, ast.Expr) and isinstance(first_item.value, ast.Str):
            return re.sub(r"[\n\\n]", "", unparse(first_item))
        return None

    def __get_arguments(self):
        ast_args = ast.iter_child_nodes(self.tree).__next__().args
        return [ast_arg.arg for ast_arg in ast_args]

    def __get_variables(self):
        variables = []
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.Assign):
                variables.extend([target.id for target in node.targets])
        return variables


if __name__ == "__main__":
    with open("/home/luiz/thoughtful_repos/support/mapper/libraries/module.py") as file:
        tree = ast.parse(file.read())
        for node in ast.iter_child_nodes(tree):
            if type(node) == ast.FunctionDef:
                fd = FunctionDef(node)
                print(fd.name, fd.arguments, fd.body, fd.calls, fd.docstring, fd.vars)
