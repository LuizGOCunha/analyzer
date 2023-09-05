from pprint import pprint
from RPA.Browser.Selenium import Selenium
import os


def func_y():
    pprint("a")


class Cls:
    """This is Cls documentation"""

    func_y()
    aaa = 20

    def __init__(self) -> None:
        self.aaa = 40
        x = func_x()
        func_y()

    def method(self):
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
