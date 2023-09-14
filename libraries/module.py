import os
from pprint import pprint

from RPA.Browser.Selenium import Selenium


def func_y():

    pprint("a")


def recursive(n, r):
    n += 1
    func_y()
    if n == 10:
        return n
    else:
        recursive(n, r)


class Cls:
    """This is Cls documentation"""

    func_y()
    aaa = 20

    def __init__(self) -> None:
        self.aaa = 40
        x = func_x()
        func_y()

    def method(self):
        self.b = Selenium()
        self.b.open_available_browser()
        self.b.set_window_size(1920, 1600)
        self.b.maximize_browser_window()
        call2()


def func_x(a: str = 0, b: str = 1):
    """
    This is a docstring
    """
    var = func_y()


def function():
    print("b")
    call2()


def call1():
    for x in range(2):
        func_y()
    b = Selenium()
    b.open_available_browser()
    b.set_window_size(1920, 1600)
    b.maximize_browser_window()
    x = Cls()
    x.method()


def call2():
    """This is call2 documentation"""
    pass


if __name__ == "__main__":
    function()
