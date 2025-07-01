x, y, t = 0, 1, 0
for i in range(10):
    t = x
    x = x+y
    y = t
    print(x)
