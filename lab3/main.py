from pathlib import Path
from explanation_compomemt import ExplanationComponent
from inference_engine import InferenceEngine
from knowledge_base import KnowledgeBase

RULES_PATH = Path(__file__).with_name("rules.json")


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} (да/нет): ").strip().lower()
        if answer in {"да", "yes", "у"}: return True
        if answer in {"нет", "no", "н"}: return False
        print("Пожалуйста, введите 'да' или 'нет'.")


def collect_initial_facts(wm) -> None:
    print("\n" + "=" * 60)
    print(" ЭКСПЕРТНАЯ СИСТЕМА ДЛЯ ПОДБОРА ФАКУЛЬТЕТА (ФРЕЙМЫ)")
    print("=" * 60)
    print("\nОтветьте на вопросы для определения подходящего факультета.\n")

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


def print_results(ie: InferenceEngine) -> None:
    print("\n" + "=" * 60)
    print(" РЕКОМЕНДАЦИИ")
    print("=" * 60)

    # Находим сработавшие правила-результаты
    recommendations = []
    for fact in ie.working_memory.facts():
        if fact.startswith("Результат = "):
            recommendations.append(fact.replace("Результат = ", ""))

    if not recommendations:
        print("\n [!] Не удалось определить факультет.")
    else:
        for rec in recommendations:
            print(f"\n >> {rec}")

            # Создаём протофрейм для компоненты объяснения
            if rec in ie.working_memory.frames:
                proto = ie.working_memory.frames[rec].create_proto_frame()
                ie.working_memory.add_proto_frame(proto)

    print("\n" + "=" * 60 + "\n")


def explanation_loop(explainer: ExplanationComponent, ie: InferenceEngine) -> None:
    print("=" * 60)
    print(" РЕЖИМ ОБЪЯСНЕНИЯ")
    print("=" * 60)
    print("\nВведите название факультета, чтобы узнать, почему он рекомендован.")
    print("Пустая строка для выхода.\n")

    while True:
        fact = input("Факультет: ").strip()
        if not fact: break
        try:
            print("\n" + "-" * 60)
            print(explainer.explain_recommendation(fact))
            print("-" * 60 + "\n")
        except Exception as error:
            print(f"[!] Ошибка: {error}\n")


def main() -> None:
    try:
        # 1. Загрузка базы знаний
        kb = KnowledgeBase.from_json(RULES_PATH)
        print(f"Загружено {len(kb.rules)} правил из {RULES_PATH.name}")

        # 2. Инициализация движка
        ie = InferenceEngine(kb)

        # 3. Строим фреймы из правил (построено N фреймов)
        ie.build_frames_from_rules()
        print(f"Построено {len(ie.working_memory.frames)} фреймов")

        # 4. Сбор фактов
        collect_initial_facts(ie.working_memory)

        # 5. Логический вывод (стратегия по умолчанию "order")
        ie.infer(strategy="order")

        # 6. Вывод результатов и создание протофреймов
        print_results(ie)

        # 7. Режим объяснения
        explainer = ExplanationComponent(ie)
        explanation_loop(explainer, ie)

        print("\n[OK] Работа системы завершена. До свидания!\n")
    except Exception as error:
        print(f"[!] Ошибка: {error}")


if __name__ == "__main__":
    main()