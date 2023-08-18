from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Union

def get_callables(path:Union[Path, str]) -> Union[list, None]:
    '''
    Get all callables from a file path
    '''
    path = Path(path)
    file_name = path.stem
    spec = spec_from_file_location(file_name, path)
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
    callables = get_callables("/this/is/a/test.py")
    if callables is not None:
        [callable() for callable in callables]
