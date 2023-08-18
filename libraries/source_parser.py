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

    def encapsulated_callables(self) -> dict:
        tree = ast.parse(source)
        internal_calls = {}
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                print(node.name)
                internal_source = "".join([astunparse.unparse(node) for node in node.body])
                unparsed_calls = re.findall(r"[a-zA-Z0-9]+\(", internal_source)
                parsed_calls = [calls[:-1] for calls in unparsed_calls]
                print(parsed_calls)
                internal_calls[node.name] = parsed_calls
        return internal_calls


if __name__ == "__main__":
    with open("libraries/mapper.py") as file:
        source = file.read()
        p = Parser(source)
        print(p.encapsulated_callables())
