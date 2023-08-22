import os


def explore(path, ignored: list = []):
    """
    Recursively explores all directories inside a given path.
    Has list of directories to be ignored, if it should prove necessary.
    Returns a dictionary with these items:
    {"path/to/directory" : [list, of, items]}
    """
    directory_map = {}

    def func(path):
        nonlocal ignored
        nonlocal directory_map
        os.chdir(path)
        path = os.getcwd()
        directory_contents = os.listdir()
        directory_map[path] = directory_contents
        print(f">> Path:", path)
        print(f">> Content:", directory_contents)
        for content in directory_contents:
            os.chdir(path)
            abs_path = os.path.join(os.getcwd(), content)
            if content in ignored:
                continue
            elif os.path.isdir(abs_path):
                func(abs_path)

    func(path)
    return directory_map


if __name__ == "__main__":
    directory_map = explore(".", ignored=[".git", "__pycache__"])
    print(directory_map)
