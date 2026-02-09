import subprocess
import sys
import os

def run_script(filename, input_data):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(file_path):
        return "", f"File '{filename}' не найден!"

    process = subprocess.Popen(
        [sys.executable, file_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    stdout, stderr = process.communicate(input=input_data)
    return stdout.strip(), stderr.strip()

def check_task_11():
    print(f"\nТестирование Задание 11: Расстояние между точками")
    test_cases = [
        ("0\n0\n3\n4", 5.0),
        ("-1\n1\n2\n5", 5.0),
        ("1\n1\n1\n4", 3.0),
        ("0\n0\n0\n0", 0.0),
        ("-1\n-2\n1\n2", 4.4721),
    ]

    failures = 0

    for i, (input_data, expected) in enumerate(test_cases, 1):
        output, error = run_script("Задание 11.py", input_data)

        if error:
            print(f"  Тест {i}: ❌ Не пройден")
            print(f"    Причина: Ошибка выполнения скрипта")
            print(f"    Детали: {error}")
            failures += 1
            continue

        try:
            val = float(output)
            if abs(val - expected) > 1e-2:
                raise AssertionError

            print(f"  Тест {i}: ✅ Пройден")
        except ValueError:
            print(f"  Тест {i}: ❌ Не пройден")
            print(f"    Причина: В выводе не числовые значения")
            print(f"    Ввод: {input_data!r}")
            print(f"    Вывод: {output!r}")
            failures += 1
        except AssertionError:
            print(f"  Тест {i}: ❌ Не пройден")
            print(f"    Причина: Неверное расстояние")
            print(f"    Ввод: {input_data!r}")
            print(f"    Ожидание: {expected}")
            print(f"    Реальность: {val}")
            failures += 1

    return failures == 0

def check_task_12():
    print(f"\nТестирование Задание 12: Площадь треугольника")
    test_cases = [
        ("0\n0\n3\n0\n0\n4", 12.0, 6.0),
        ("1\n1\n2\n5\n5\n3", 12.2, 7.0),
        ("0\n0\n10\n0\n5\n5", 24.14, 25.0),
    ]

    failures = 0

    for i, (input_data, exp_perimeter, exp_area) in enumerate(test_cases, 1):
        output, error = run_script("Задание 12.py", input_data)

        if error:
            print(f"  Тест {i}: ❌ Не пройден")
            print(f"    Причина: Ошибка выполнения скрипта")
            print(f"    Детали: {error}")
            failures += 1
            continue

        parts = output.split()
        try:
            if len(parts) != 2:
                raise ValueError("Вывод должен содержать два числа!")

            p_val = float(parts[0])
            s_val = float(parts[1])

            p_ok = abs(p_val - exp_perimeter) <= 0.1
            s_ok = abs(s_val - exp_area) <= 0.1

            if not (p_ok and s_ok):
                raise AssertionError

            print(f"  Тест {i}: ✅ Пройден")

        except ValueError as e:
            print(f"  Тест {i}: ❌ Не пройден")
            print(f"    Причина: {str(e)}")
            print(f"    Ввод: {input_data!r}")
            print(f"    Вывод: {output!r}")
            failures += 1
        except AssertionError:
            print(f"  Тест {i}: ❌ Не пройден")
            print(f"    Причина: Некорректные значения")
            print(f"    Ввод: {input_data!r}")
            print(f"    Ожидание: Периметр ~ {exp_perimeter}, Площадь ~ {exp_area}")
            print(f"    Реальность: Периметр = {parts[0]}, Площадь = {parts[1]}")
            failures += 1

    return failures == 0

if __name__ == '__main__':
    success_11 = check_task_11()
    success_12 = check_task_12()

    if not (success_11 and success_12):
        print("\nНе все тесты пройдены ❌")
        sys.exit(1)
    else:
        print("\nВсе тесты пройдены ✅")
        sys.exit(0)