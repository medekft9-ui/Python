a = int(input())
b = int(input())
c = int(input())
if a + b <= c or a + c <= b or b + c <= a:
    print("Не существует")
else:
    if a >= b and a >= c:
        bolshaya = a
        mal1 = b
        mal2 = c
    elif b >= a and b >= c:
        bolshaya = b
        mal1 = a
        mal2 = c
    else:
        bolshaya = c
        mal1 = a
        mal2 = b
    if bolshaya * bolshaya == mal1 * mal1 + mal2 * mal2:
        print("Прямоугольный")
    elif bolshaya * bolshaya < mal1 * mal1 + mal2 * mal2:
        print("Остроугольный")
    else:
        print("Тупоугольный")