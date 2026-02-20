def f(x, n):
    s = 0
    for i in range(n):
        s += x**4 - 16 * x**2 + 5*x
    return s / 2 / n



for n in range(1, 100):
    print(f(-2.903534, n))
