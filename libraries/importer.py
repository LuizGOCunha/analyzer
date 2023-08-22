from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Union


def get_callables(path: Union[Path, str]) -> Union[list, None]:
    """
    Get all callables from a file path
    Be aware that it must be an absolute path
    """
    path = Path(path)
    file_name = path.stem
    spec = spec_from_file_location(file_name, path)
    if spec is None:
        return None
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError:
        return None
    names = dir(module)
    callables = []
    for name in names:
        try:
            attribute = getattr(module, name)
        except AttributeError:
            continue
        if callable(attribute):
            callables.append(attribute)
    return callables


if __name__ == "__main__":
    callables = get_callables("/home/luiz/thoughtful_repos/support/mapper/libraries/module.py")
    print(callables)
