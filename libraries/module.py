from pprint import pprint


class Cls:
    def __init__(self) -> None:
        func_x()
        func_y()

    def method(self):
        call1()
        x = call2()


def func_x():
    func_y()


def func_y():
    pprint("a")


def function():
    call1()
    call2()


def call1():
    pass


def call2():
    pass


function()

{function: {call1: {}, call2: {}}}
