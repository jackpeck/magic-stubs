# coding: magic_stubs

def double_wrapper(f):
    return lambda x: f(x) * 2

print(str(double_wrapper(lambda x: x**2)(4)))