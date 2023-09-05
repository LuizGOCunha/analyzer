import re
import ast
import astunparse
from pathlib import Path
from models.function_def import FunctionMd
from models.class_def import ClassMd


class Parser:
    callable_pattern = r"[a-zA-Z0-9_.]+\("

    def __init__(self, path) -> None:
        # Should receive path, remove source internally
        if isinstance(path, str):
            path = Path(path)
        with open(path) as file:
            self.source = file.read()
        self.ast_nodes, self.imports, self.functions, self.classes = self.__get_logic_nodes()

    @property
    def all_callables(self):
        pattern = re.compile(self.callable_pattern)
        callables = re.findall(pattern, self.source)
        return [callable[:-1] for callable in callables]

    def __get_call_names_from_node(self, node):
        internal_source = "".join([astunparse.unparse(node) for node in node.body])
        unparsed_calls = re.findall(self.callable_pattern, internal_source)
        parsed_calls = [calls[:-1] for calls in unparsed_calls]
        return parsed_calls

    def encapsulated_callables(self) -> dict:
        tree = ast.parse(self.source)
        internal_calls = {}
        for node in ast.iter_child_nodes(tree):
            # Right now only identifies functions
            if isinstance(node, ast.FunctionDef):
                parsed_calls = self.__get_call_names_from_node(node)
                internal_calls[node.name] = parsed_calls
            elif isinstance(node, ast.ClassDef):
                # Add ClassMD, then remove methods from it and add them
                class_name = node.name
                for int_node in node.body:
                    if isinstance(int_node, ast.FunctionDef):
                        parsed_calls = self.__get_call_names_from_node(int_node)
                        method_name = int_node.name
                        internal_calls[f"{class_name}.{method_name}"] = parsed_calls
        return internal_calls

    def __get_logic_nodes(self):
        """
        Returns a tuple of a source, each items is a list containing:
        (All_nodes, importations, function_definitons, class_definitions)
        """
        tree = ast.parse(self.source)
        ast_nodes = []
        func_nodes = []
        class_nodes = []
        import_nodes = []
        for node in ast.iter_child_nodes(tree):
            ast_nodes.append(node)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
            elif isinstance(node, ast.FunctionDef):
                func_nodes.append(FunctionMd(node))
            elif isinstance(node, ast.ClassDef):
                class_nodes.append(ClassMd(node))
        return (ast_nodes, import_nodes, func_nodes, class_nodes)


if __name__ == "__main__":
    p = Parser("libraries/module.py")
    print(p.functions)
    print(p.classes)
    # print(p.encapsulated_callables())
