from pathlib import Path
from typing import Dict, Tuple

from explanation import ExplanationComponent
from inference_engine import InferenceEngine
from knowledge_base import KnowledgeBase
from working_memory import WorkingMemory

# Путь к файлу с правилами (в той же директории)
RULES_PATH = Path(__file__).with_name("rules.json")


def ask_yes_no(prompt: str) -> bool:
    """
    Запрашивает ответ да/нет у пользователя.

    Args:
        prompt: Текст вопроса

    Returns:
        True для положительного ответа, False для отрицательного
    """
    while True:
        answer = input(f"{prompt} (да/нет): ").strip().lower()
        if answer in {"да", "д", "yes", "y"}:
            return True
        if answer in {"нет", "н", "no", "n"}:
            return False
        print("Пожалуйста, введите 'да' или 'нет'.")


def ask_int(prompt: str, min_value: int = None, max_value: int = None) -> int:
    """
    Запрашивает целое число у пользователя.

    Args:
        prompt: Текст вопроса
        min_value: Минимально допустимое значение (необязательно)
        max_value: Максимально допустимое значение (необязательно)

    Returns:
        Введенное целое число
    """
    while True:
        value = input(f"{prompt}: ").strip()
        try:
            num = int(value)
            if min_value is not None and num < min_value:
                print(f"Значение должно быть не меньше {min_value}.")
                continue
            if max_value is not None and num > max_value:
                print(f"Значение должно быть не больше {max_value}.")
                continue
            return num
        except ValueError:
            print("Введите целое число.")


def collect_initial_facts(wm: WorkingMemory) -> None:
    """
    Собирает исходные факты на основе ответов пользователя.

    Задает вопросы о интересах, возрасте и среднем балле,
    и добавляет соответствующие факты в рабочую память.

    Args:
        wm: Рабочая память для добавления фактов
    """
    print("\n" + "=" * 60)
    print("  ЭКСПЕРТНАЯ СИСТЕМА ДЛЯ ПОДБОРА ФАКУЛЬТЕТА")
    print("=" * 60)
    print("\nОтветьте на вопросы для определения подходящего факультета.\n")

    # Запрос интересов
    print("--- ИНТЕРЕСЫ ---")

    interests = {
        "математике": "Есть ли у вас интерес к математике?",
        "программированию": "Есть ли у вас интерес к программированию?",
        "дизайну": "Есть ли у вас интерес к дизайну?",
        "управлению": "Есть ли у вас интерес к управлению?",
        "экономике": "Есть ли у вас интерес к экономике?",
    }

    for interest, question in interests.items():
        answer = "да" if ask_yes_no(question) else "нет"
        wm.add_fact(f"Интерес к {interest} = {answer}", "user")

    print("\n" + "=" * 60)
    print("Спасибо! Обрабатываю ваши ответы...")
    print("=" * 60 + "\n")


def choose_strategy() -> str:
    """
    Позволяет пользователю выбрать стратегию разрешения конфликтов.

    Returns:
        Идентификатор выбранной стратегии (order, specificity, recency)
    """
    strategies: Dict[str, Tuple[str, str]] = {
        "1": ("order", "По порядку правил в базе знаний"),
        "2": ("specificity", "По специфичности (больше условий = выше приоритет)"),
        "3": ("recency", "По недавности фактов в условиях правила"),
    }

    print("\nВыберите стратегию разрешения конфликтов:")
    print("-" * 60)
    for key, (_, description) in strategies.items():
        print(f"  {key}. {description}")
    print("-" * 60)

    while True:
        choice = input("Ваш выбор [1-3]: ").strip()
        if choice in strategies:
            selected_name = strategies[choice][1]
            print(f"\nВыбрана стратегия: {selected_name}\n")
            return strategies[choice][0]
        print("Недопустимый выбор, повторите ввод.")


def print_results(wm: WorkingMemory) -> None:
    """
    Выводит все полученные факты и итоговые рекомендации.

    Args:
        wm: Рабочая память с фактами
    """
    print("\n" + "=" * 60)
    print("  ПОЛУЧЕННЫЕ ФАКТЫ")
    print("=" * 60)

    for record in wm.items():
        source = "пользователь" if record.source == "user" else f"правило {record.source}"
        print(f"  - {record.fact} (источник: {source})")

    # Выделяем итоговые рекомендации
    recommendations = [fact for fact in wm.facts() if fact.startswith("Результат = ")]

    print("\n" + "=" * 60)
    print("  РЕКОМЕНДАЦИИ")
    print("=" * 60)

    if recommendations:
        for fact in recommendations:
            result = fact.replace("Результат = ", "")
            print(f"\n  >> {result}")
    else:
        print("\n  [!] Не удалось определить факультет.")
        print("      Попробуйте изменить исходные данные.")

    print("\n" + "=" * 60 + "\n")


def print_applied_rules(applied_rules) -> None:
    """
    Выводит информацию о сработавших правилах.

    Args:
        applied_rules: Список примененных правил
    """
    if applied_rules:
        print("=" * 60)
        print("  СРАБОТАВШИЕ ПРАВИЛА (в порядке применения)")
        print("=" * 60)
        for applied in applied_rules:
            print(f"  {applied.iteration}. {applied.rule.id}: {applied.rule.conclusion}")
        print("=" * 60 + "\n")
    else:
        print("\n⚠️  Ни одно правило не сработало.\n")


def explanation_loop(explainer: ExplanationComponent) -> None:
    """
    Интерактивный цикл для запроса объяснений фактов.

    Позволяет пользователю запрашивать объяснения для различных фактов,
    пока он не введет пустую строку.

    Args:
        explainer: Компонента объяснения
    """
    print("=" * 60)
    print("  РЕЖИМ ОБЪЯСНЕНИЯ")
    print("=" * 60)
    print("\nВведите интересующий факт для получения объяснения.")
    print("Пустая строка для выхода.\n")

    while True:
        fact = input("Факт: ").strip()
        if not fact:
            break
        try:
            print("\n" + "-" * 60)
            print(explainer.explain(fact))
            print("-" * 60 + "\n")
        except ValueError as error:
            print(f"[!] Ошибка: {error}\n")


def main() -> None:
    """
    Главная функция программы.

    Выполняет следующие шаги:
    1. Загружает базу знаний из JSON-файла
    2. Собирает исходные факты от пользователя
    3. Выбирает стратегию разрешения конфликтов
    4. Выполняет логический вывод
    5. Выводит результаты и объяснения
    """
    try:
        # Загрузка базы знаний
        kb = KnowledgeBase.from_json(RULES_PATH)

        # Инициализация рабочей памяти и сбор фактов
        wm = WorkingMemory()
        collect_initial_facts(wm)

        # Выбор стратегии разрешения конфликтов
        strategy = choose_strategy()

        # Запуск механизма вывода
        engine = InferenceEngine(kb)
        applied_rules = engine.infer(wm, strategy=strategy)

        # Вывод сработавших правил
        print_applied_rules(applied_rules)

        # Вывод результатов
        print_results(wm)

        # Режим объяснения
        explainer = ExplanationComponent(wm)
        explanation_loop(explainer)

        print("\n[OK] Работа системы завершена. До свидания!\n")

    except FileNotFoundError as error:
        print(f"[!] Ошибка: {error}")
    except Exception as error:
        print(f"[!] Неожиданная ошибка: {error}")


if __name__ == "__main__":
    main()
