#!/usr/bin/python

ket=raw_input("Enter your ket: ")
ket=[int(i) for i in ket.split()]

def sign(value):
    if value > 0:
        return "+" + str(value)
    if value <= 0:
        return str(value)

def ldown(*args):
    for a in args:
        coef = a[0]*(a[0]+1)-a[1]*(a[1]-1)
        print("L-(|{}, {}>) = sqrt({}) |{}, {}>".format(a[0], sign(a[1]), coef, a[0], sign(a[1]-1)))
    return

def lup(*args):
    for a in args:
        coef = a[0]*(a[0]+1)-a[1]*(a[1]+1)
        print("L+(|{}, {}>) = sqrt({}) |{}, {}>".format(a[0], sign(a[1]), coef, a[0], sign(a[1]+1)))
    return

ldown(ket)
lup(ket)
