from pyccel.decorators import types

@types('double','double','double')
def fun(xi1, xi2, xi3):
    from user_mod import user_func
    return user_func(xi1, xi2, xi3)

print(fun(1.0,2.0,3.0))

