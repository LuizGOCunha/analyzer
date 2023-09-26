class UnknownFuncMd:
    """
    Function model to be used when the functions source is not known
    """
    calls = []

    def __init__(self, name) -> None:
        self.name = name
