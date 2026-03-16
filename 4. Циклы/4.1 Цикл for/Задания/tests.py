import os
import sys
from typing import Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")

from tester import TaskConfig, TestCase, exact_match, run_module

_BASE_DIR = os.path.dirname(__file__)


def _make_multiplication_table(n: int) -> str:
    return "\n".join(f"{n} * {i} = {n * i}" for i in range(1, 11))


def _make_staircase(n: int) -> str:
    return "\n".join("".join(str(j) for j in range(1, i + 1)) for i in range(1, n + 1))


def _make_staircase2(n: int) -> str:
    return "\n".join("".join(str(j) for j in range(n, i - 1, -1)) for i in range(1, n + 1))


def _make_triangle_seq(n: int) -> str:
    result = []
    k = 1
    while len(result) < n:
        for _ in range(k):
            if len(result) >= n:
                break
            result.append(str(k))
        k += 1
    return " ".join(result)


def _pythagorean_validator(output: str, expected: int) -> Tuple[bool, str]:
    n = expected
    lines = output.strip().split("\n")
    if len(lines) != n:
        return False, f"Ожидалось {n} строк, получено {len(lines)}"
    for i, line in enumerate(lines, 1):
        nums = line.split()
        if len(nums) != n:
            return False, f"Строка {i}: ожидалось {n} чисел, получено {len(nums)}"
        for j, num in enumerate(nums, 1):
            expected_val = i * j
            try:
                actual_val = int(num)
            except ValueError:
                return False, f"Строка {i}, колонка {j}: не число: {num!r}"
            if actual_val != expected_val:
                return False, f"Строка {i}, колонка {j}: ожидалось {expected_val}, получено {actual_val}"
    return True, ""


TASKS = [
    TaskConfig(
        task_id="41",
        name="Факториал",
        filename="Задание 41.py",
        time_limit=5.0,
        memory_limit_bytes=64 * 1024 * 1024,
        forbidden_constructs=[],
        check_pep8=True,
        validator=exact_match,
        test_cases=[
            TestCase("1", "1"),
            TestCase("2", "2"),
            TestCase("3", "6"),
            TestCase("4", "24"),
            TestCase("5", "120"),
            TestCase("6", "720"),
            TestCase("7", "5040"),
            TestCase("10", "3628800"),
            TestCase("12", "479001600"),
        ],
    ),
    TaskConfig(
        task_id="42",
        name="Таблица умножения",
        filename="Задание 42.py",
        time_limit=5.0,
        memory_limit_bytes=64 * 1024 * 1024,
        forbidden_constructs=[],
        check_pep8=True,
        validator=exact_match,
        test_cases=[
            TestCase("5", _make_multiplication_table(5)),
            TestCase("1", _make_multiplication_table(1)),
            TestCase("3", _make_multiplication_table(3)),
            TestCase("7", _make_multiplication_table(7)),
            TestCase("9", _make_multiplication_table(9)),
            TestCase("10", _make_multiplication_table(10)),
        ],
    ),
    TaskConfig(
        task_id="43",
        name="Лесенка",
        filename="Задание 43.py",
        time_limit=5.0,
        memory_limit_bytes=64 * 1024 * 1024,
        forbidden_constructs=[],
        check_pep8=True,
        validator=exact_match,
        test_cases=[
            TestCase("1", _make_staircase(1)),
            TestCase("2", _make_staircase(2)),
            TestCase("3", _make_staircase(3)),
            TestCase("4", _make_staircase(4)),
            TestCase("5", _make_staircase(5)),
            TestCase("9", _make_staircase(9)),
        ],
    ),
    TaskConfig(
        task_id="44",
        name="Лесенка 2",
        filename="Задание 44.py",
        time_limit=5.0,
        memory_limit_bytes=64 * 1024 * 1024,
        forbidden_constructs=[],
        check_pep8=True,
        validator=exact_match,
        test_cases=[
            TestCase("1", _make_staircase2(1)),
            TestCase("2", _make_staircase2(2)),
            TestCase("3", _make_staircase2(3)),
            TestCase("4", _make_staircase2(4)),
            TestCase("5", _make_staircase2(5)),
            TestCase("9", _make_staircase2(9)),
        ],
    ),
    TaskConfig(
        task_id="45",
        name="Таблица Пифагора",
        filename="Задание 45.py",
        time_limit=5.0,
        memory_limit_bytes=64 * 1024 * 1024,
        forbidden_constructs=[],
        check_pep8=True,
        validator=_pythagorean_validator,
        test_cases=[
            TestCase("1", 1),
            TestCase("2", 2),
            TestCase("3", 3),
            TestCase("4", 4),
            TestCase("5", 5),
            TestCase("10", 10),
        ],
    ),
    TaskConfig(
        task_id="416",
        name="Треугольная последовательность",
        filename="Задание 416.py",
        time_limit=5.0,
        memory_limit_bytes=64 * 1024 * 1024,
        forbidden_constructs=[],
        check_pep8=True,
        validator=exact_match,
        test_cases=[
            TestCase("1", "1"),
            TestCase("2", "1 2"),
            TestCase("3", _make_triangle_seq(3)),
            TestCase("5", "1 2 2 3 3"),
            TestCase("6", _make_triangle_seq(6)),
            TestCase("7", _make_triangle_seq(7)),
            TestCase("10", _make_triangle_seq(10)),
            TestCase("15", _make_triangle_seq(15)),
        ],
    ),
]

if __name__ == "__main__":
    result = run_module("Цикл for", TASKS, _BASE_DIR)
    sys.exit(0 if result.solved_tasks == result.total_tasks else 1)
