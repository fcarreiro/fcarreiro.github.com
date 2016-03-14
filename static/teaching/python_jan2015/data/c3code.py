def is_even(n):
    if n % 2 == 0:
        return True
    else:
        return False

def average(n, m):
    thesum = float(n + m)
    return thesum/2

def cat_twice_and_print(part1, part2):
    cat = part1 + part2
    print_twice(cat)

def print_twice(msg):
    print msg
    print msg

# calculates n * m (in a complicated way)
def multiply(n, m):
    if n == 0:
        return 0
    else:
        return m + multiply(n - 1, m)

def fib(n):
    if n == 0 or n == 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)

def reverse_string(s):
    return reverse_from_n(s, 0)

def reverse_from_n(s, i):
    if i == len(s):
        return ''
    else:
        return reverse_from_n(s, i+1) + s[i]

def collatz(n):
    if n == 1:
        return 0
    elif n % 2 == 0:
        return 1 + collatz(n/2)
    else:
        return 1 + collatz(3*n+1)

def sum_up_to(n):
    i = 1
    v = 0
    while i <= n:
        v = v + i
        i = i + 1
    return v

def count(c, sentence):
    i = 0; n = 0
    while i < len(sentence):
        if sentence[i] == c: n = n + 1
        i = i + 1
    return n