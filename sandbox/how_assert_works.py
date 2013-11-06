from types import IntType

def add(a,b):
    add_up = a+b
    return add_up

def main():
    s = add(2, 5)
    assert s == 10

main()
