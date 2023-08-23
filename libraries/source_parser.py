import re
import ast
import astunparse


class Parser:
    def __init__(self, source: str) -> None:
        self.source = source

    @property
    def all_callables(self):
        pattern = re.compile(r"\s[a-zA-Z]+\(")
        callables = re.findall(pattern, self.source)
        return [callable[:-1] for callable in callables]

    def __get_call_names_from_node(self, node):
        internal_source = "".join([astunparse.unparse(node) for node in node.body])
        unparsed_calls = re.findall(r"[a-zA-Z0-9]+\(", internal_source)
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
                class_name = node.name
                for int_node in node.body:
                    if isinstance(int_node, ast.FunctionDef):
                        parsed_calls = self.__get_call_names_from_node(int_node)
                        method_name = int_node.name
                        internal_calls[f"{class_name}.{method_name}"] = parsed_calls
        return internal_calls


if __name__ == "__main__":
    with open("libraries/module.py") as file:
        source = file.read()
        p = Parser(source)
        print(p.encapsulated_callables())
