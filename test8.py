# coding: magic_python_english

# def double_wrapper(f):
#     return lambda x: f(x) * 2

# print(str(double_wrapper(lambda x: x**2)(4)))



class Foo:
    def bar():
        # return 4
        pass

a = Foo()
print(a.bar())