def func_x():
    func_y()


from pprint import pprint


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
