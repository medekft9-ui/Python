a = int(input())
b = int(input())
c = int(input())
if a + b <= c or a + c <= b or b + c <= a:
    print("Не существует")
else:
    h = max(a, b, c)
    c1 = min(a, b, c)
    c2 = (a + b + c) - (h + c1)

    if h ** 2 == c1 ** 2 + c2 ** 2:
        print("Прямоугольный")
    elif h ** 2 < c1 ** 2 + c2 ** 2:
        print("Остроугольный")
    else:
        print("Тупоугольный")
