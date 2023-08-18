def func1():
    pass

def func():
    x=1
    func1()

from trace import Trace
trcer = Trace()
trcer.runfunc(func)
