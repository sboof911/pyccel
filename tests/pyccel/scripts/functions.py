# pylint: disable=missing-function-docstring, missing-module-docstring

#$ header function incr_(int)
def incr_(x):
    #$ header function decr_(int)
    def decr_(y):
        y = y-1
        return y
    x = x + 1
    return x

def helloworld():
    print('hello world')

#$ header function incr(int)
def incr(x):
    x = x + 1
    return x

#$ header function decr(int) results(int)
def decr(x):
    y = x - 1
    return y

#$ header function incr_array(int [:])
def incr_array(x):
    x[:] = x + 1

y_=[1,2,3]

# #$ header function decr_array([int]) results([int])
# def decr_array(x):
#     y_[1] = 6
#     z = y_
#     t = y_+x
#     return t

#$ header function decr_array(int [:])
def decr_array(x):
    x[:] = x - 1

#$ header function f1(int, int, int) results(int)
def f1(x, n=2, m=3):
    y = x - n*m
    return y

#$ header function f2(int, int) results(int)
def f2(x, m=None):
    if m is None:
        y = x + 1
    else:
        y = x - 1
    return y

y = decr(2)
z = f1(1)

z1 = f2(1)
z2 = f2(1, m=0)

helloworld()

def pass_fun():
    pass

if __name__ == '__main__':
    print(y_)
    print(y)
    print(z)
    print(z1)
    print(z2)
