import ast
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Структуры данных
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    """Один тест-кейс: входные данные и ожидаемый результат."""
    input_data: str
    expected: Any


@dataclass
class TaskConfig:
    """Конфигурация проверки одного задания."""
    task_id: str
    name: str
    filename: str
    test_cases: List[TestCase]
    validator: Callable[[str, Any], Tuple[bool, str]]

    time_limit: float = 10.0
    memory_limit_bytes: int = 128 * 1024 * 1024
    forbidden_constructs: List[str] = field(default_factory=list)
    check_pep8: bool = True


class TaskResult:
    def __init__(self, task_id: str, name: str) -> None:
        self.task_id = task_id
        self.name = name
        self.total_tests: int = 0
        self.passed_tests: int = 0
        self.has_forbidden: bool = False
        self.pep8_issues: List[str] = []

    @property
    def is_solved(self) -> bool:
        return (
            self.total_tests > 0
            and self.passed_tests == self.total_tests
            and not self.has_forbidden
            and not self.pep8_issues
        )

    @property
    def percentage(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests * 100.0


class ModuleResult:
    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.task_results: List[TaskResult] = []

    @property
    def total_tasks(self) -> int:
        return len(self.task_results)

    @property
    def solved_tasks(self) -> int:
        return sum(1 for r in self.task_results if r.is_solved)

    @property
    def total_tests(self) -> int:
        return sum(r.total_tests for r in self.task_results)

    @property
    def passed_tests(self) -> int:
        return sum(r.passed_tests for r in self.task_results)

    @property
    def percentage(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.solved_tasks / self.total_tasks * 100.0


# ---------------------------------------------------------------------------
# Внутренние проверки
# ---------------------------------------------------------------------------

def _run_script(
    file_path: str,
    input_data: str,
    time_limit: float,
    memory_limit_bytes: int,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Запускает Python-скрипт с заданным вводом.
    Возвращает (stdout, error_msg). При успехе error_msg is None.
    """
    if not os.path.exists(file_path):
        return None, f"Файл не найден: {os.path.basename(file_path)}"

    if os.path.getsize(file_path) == 0:
        return None, "Файл пустой — решение не написано"

    try:
        process = subprocess.Popen(
            [sys.executable, file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    except Exception as exc:
        return None, f"Ошибка запуска: {exc}"

    memory_exceeded = [False]

    if _PSUTIL_AVAILABLE and memory_limit_bytes > 0:
        def _monitor(pid: int, limit_bytes: int, flag: list) -> None:
            try:
                ps = psutil.Process(pid)
                while True:
                    try:
                        if ps.memory_info().rss > limit_bytes:
                            flag[0] = True
                            ps.kill()
                            return
                    except psutil.NoSuchProcess:
                        return
                    time.sleep(0.05)
            except Exception:
                return

        t = threading.Thread(
            target=_monitor,
            args=(process.pid, memory_limit_bytes, memory_exceeded),
            daemon=True,
        )
        t.start()

    try:
        stdout, stderr = process.communicate(input=input_data, timeout=time_limit)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return None, f"Превышен лимит времени ({time_limit} с)"

    if memory_exceeded[0]:
        limit_mb = memory_limit_bytes / (1024 * 1024)
        return None, f"Превышен лимит памяти ({limit_mb:.0f} МБ / {memory_limit_bytes} байт)"

    if stderr.strip():
        first_line = stderr.strip().splitlines()[-1]
        return None, f"Ошибка выполнения: {first_line}"

    return stdout.strip(), None


def _check_forbidden_constructs(file_path: str, forbidden: List[str]) -> List[str]:
    """
    Проверяет исходный код на наличие запрещённых AST-конструкций.
    Возвращает список найденных запрещённых конструкций.
    """
    if not forbidden:
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        if not source.strip():
            return []
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as exc:
        return [f"Синтаксическая ошибка при парсинге: {exc}"]
    except Exception as exc:
        return [f"Ошибка парсинга: {exc}"]

    found = set()
    for node in ast.walk(tree):
        node_type = type(node).__name__
        if node_type in forbidden:
            found.add(node_type)

    return sorted(found)


def _check_pep8(file_path: str) -> List[str]:
    """
    Запускает flake8 на файле.
    Возвращает список замечаний (пустой список — всё OK).
    """
    if os.path.getsize(file_path) == 0:
        return []

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "flake8",
                "--max-line-length=120",
                file_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            return []
        lines = [ln.strip() for ln in result.stdout.strip().splitlines() if ln.strip()]
        return [ln.replace(file_path, os.path.basename(file_path)) for ln in lines]
    except FileNotFoundError:
        return ["flake8 не установлен (pip install flake8)"]
    except Exception as exc:
        return [f"Ошибка запуска flake8: {exc}"]


# ---------------------------------------------------------------------------
# Основные функции запуска
# ---------------------------------------------------------------------------

def run_task(config: TaskConfig, base_dir: str) -> TaskResult:
    """Проверяет одно задание и возвращает TaskResult."""
    result = TaskResult(config.task_id, config.name)
    file_path = os.path.join(base_dir, config.filename)

    print(f"\n{'=' * 60}")
    print(f"  Задание {config.task_id}: {config.name}")
    print(f"{'=' * 60}")

    file_exists = os.path.exists(file_path)

    # --- Статические проверки ---
    if file_exists and os.path.getsize(file_path) > 0:

        # 1. Запрещённые конструкции (AST)
        if config.forbidden_constructs:
            forbidden_found = _check_forbidden_constructs(file_path, config.forbidden_constructs)
            if forbidden_found:
                result.has_forbidden = True
                names = ", ".join(forbidden_found)
                print(f"  ⛔ Запрещённые конструкции: {names}")
            else:
                allowed = ", ".join(config.forbidden_constructs)
                print(f"  ✅ AST: запрещённые конструкции [{allowed}] не найдены")

        # 2. PEP 8 / flake8
        if config.check_pep8:
            pep8_issues = _check_pep8(file_path)
            result.pep8_issues = pep8_issues
            if pep8_issues:
                print(f"  ⚠️  PEP 8 / flake8 ({len(pep8_issues)} замечаний):")
                for issue in pep8_issues:
                    print(f"       {issue}")
            else:
                print(f"  ✅ PEP 8: OK")

    elif not file_exists:
        print(f"  ❌ Файл не найден: {config.filename}")
    else:
        print(f"  ℹ️  Файл пустой — решение не написано")

    # --- Динамические тесты ---
    print(f"\n  Тесты ({len(config.test_cases)}):")

    for i, tc in enumerate(config.test_cases, 1):
        result.total_tests += 1
        output, error = _run_script(
            file_path, tc.input_data, config.time_limit, config.memory_limit_bytes
        )

        if error is not None:
            print(f"    Тест {i}: ❌  {error}")
            _print_io(tc.input_data, tc.expected)
            continue

        passed, reason = config.validator(output, tc.expected)
        if passed:
            result.passed_tests += 1
            print(f"    Тест {i}: ✅  Пройден")
        else:
            print(f"    Тест {i}: ❌  {reason}")
            _print_io(tc.input_data, tc.expected, output)

    pct = result.percentage
    bar = _progress_bar(pct)
    print(
        f"\n  Результат: {result.passed_tests}/{result.total_tests} тестов  "
        f"{bar}  {pct:.0f}%"
    )

    return result


def run_module(
    module_name: str,
    tasks: List[TaskConfig],
    base_dir: str,
) -> ModuleResult:
    """Проверяет все задания модуля и выводит итоговую статистику."""
    module_result = ModuleResult(module_name)

    print(f"\n{'#' * 60}")
    print(f"  Модуль: {module_name}")
    print(f"{'#' * 60}")

    for config in tasks:
        task_result = run_task(config, base_dir)
        module_result.task_results.append(task_result)

    # Итог по модулю
    pct = module_result.percentage
    bar = _progress_bar(pct)

    print(f"\n{'=' * 60}")
    print(f"  ИТОГО по модулю «{module_name}»")
    print(f"{'=' * 60}")

    for tr in module_result.task_results:
        task_bar = _progress_bar(tr.percentage, width=10)
        flag = " ⛔" if tr.has_forbidden else ""
        print(
            f"  Задание {tr.task_id}: {task_bar} {tr.percentage:.0f}%"
            f"  ({tr.passed_tests}/{tr.total_tests}){flag}"
        )

    print(f"\n  Тесты:   {module_result.passed_tests}/{module_result.total_tests} пройдено")
    print(f"  Решено:  {module_result.solved_tasks}/{module_result.total_tasks} заданий")
    print(f"  Прогресс модуля: {bar}  {pct:.0f}%")
    print(f"{'=' * 60}\n")

    return module_result


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _progress_bar(pct: float, width: int = 20) -> str:
    filled = round(pct / 100 * width)
    filled = max(0, min(filled, width))
    return f"[{'█' * filled}{'░' * (width - filled)}]"


def _print_io(
    input_data: str,
    expected: Any,
    actual: Optional[str] = None,
) -> None:
    indent = "         "
    if input_data:
        indented = input_data.replace("\n", f"\n{indent}    ")
        print(f"{indent}Ввод:\n{indent}    {indented}")
    print(f"{indent}Ожидание:\n{indent}    {expected}")
    if actual is not None:
        print(f"{indent}Факт:\n{indent}    {actual}")


# ---------------------------------------------------------------------------
# Встроенные валидаторы
# ---------------------------------------------------------------------------

def exact_match(output: str, expected: Any) -> Tuple[bool, str]:
    """Точное строковое совпадение."""
    exp_str = str(expected)
    if output == exp_str:
        return True, ""
    return False, "Вывод не совпадает с ожидаемым"


def float_close(tolerance: float = 1e-2) -> Callable[[str, Any], Tuple[bool, str]]:
    """Одно вещественное число с допустимой погрешностью."""
    def _validator(output: str, expected: Any) -> Tuple[bool, str]:
        try:
            val = float(output)
        except ValueError:
            return False, f"Вывод не является числом: {output!r}"
        if abs(val - float(expected)) <= tolerance:
            return True, ""
        return False, f"Числа не совпадают (допуск ±{tolerance}): {val} ≠ {expected}"
    return _validator


def multi_value(
    *specs: Tuple[type, Optional[float]],
    sep: Optional[str] = None,
) -> Callable[[str, Any], Tuple[bool, str]]:
    """
    Валидатор для нескольких значений в одной строке.

    specs: пары (тип, допуск_или_None).
      - Если допуск is None — точное сравнение через ==.
      - Если допуск float — сравнение |a - b| <= допуск.

    Пример:
      multi_value((float, 0.1), (float, 0.1))   # два float с погрешностью 0.1
      multi_value((int, None), (int, None))       # два int, точно
    """
    def _validator(output: str, expected: Any) -> Tuple[bool, str]:
        parts = output.split(sep)
        if len(parts) != len(specs):
            return (
                False,
                f"Ожидалось {len(specs)} значений, получено {len(parts)}: {output!r}",
            )
        for idx, ((type_func, tol), exp_val, part) in enumerate(
            zip(specs, expected, parts), 1
        ):
            part = part.strip()
            try:
                val = type_func(part)
            except (ValueError, TypeError):
                return (
                    False,
                    f"Значение #{idx} ({part!r}) не преобразуется к {type_func.__name__}",
                )
            exp_cast = type_func(exp_val)
            if tol is not None:
                if abs(val - exp_cast) > tol:
                    return False, f"Значение #{idx}: ожидалось {exp_cast}, получено {val}"
            else:
                if val != exp_cast:
                    return False, f"Значение #{idx}: ожидалось {exp_cast}, получено {val}"
        return True, ""
    return _validator
