import ast
import inspect
from pprint import pprint
from module import func_x


def mapper(func):
    map = {}

    def get_called_functions(func, map):
        source_lines, _ = inspect.getsourcelines(func)
        source_code = "".join(source_lines)
        tree = ast.parse(source_code)

        map[func] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                function_name = node.func.id
                print(function_name)
                function_object = globals().get(function_name)
                if function_object and callable(function_object):
                    print("got it")
                    map[func].update({function_object: {}})
                    get_called_functions(function_object, map[func])
        return map

    return get_called_functions(func, map)


def func2():
    pprint("a")
    func_x()


def func3():
    func2()


def func1():
    func2()
    func3()


if __name__ == "__main__":
    called_functions = mapper(func1)
    pprint(called_functions)
