from dataclasses import dataclass
from typing import List, Sequence

from knowledge_base import KnowledgeBase, Rule
from working_memory import WorkingMemory
from Frame import Frame, Slot

ConflictStrategy = str


@dataclass
class AppliedRule:
    """
    Информация о примененном правиле.

    Attributes:
        rule: Примененное правило
        iteration: Номер итерации, на которой правило сработало
    """
    rule: Rule
    iteration: int


class InferenceEngine:
    """
    Механизм логического вывода для продукционной экспертной системы.

    Реализует прямой вывод с несколькими стратегиями разрешения конфликтов:
    - order: применение правил в порядке объявления в базе знаний
    - specificity: приоритет правилам с большим числом условий
    - recency: приоритет правилам с более свежими фактами в условиях
    """

    def __init__(self, knowledge_base: KnowledgeBase) -> None:
        """
        Инициализирует механизм вывода.

        Args:
            knowledge_base: База знаний с правилами
        """
        self._kb = knowledge_base
        # Создаем рабочую память прямо здесь, чтобы компонента объяснения имела к ней доступ
        self.working_memory = WorkingMemory()

    def infer(
            self,
            strategy: ConflictStrategy = "order"
    ) -> List[AppliedRule]:
        """
        Выполняет прямой вывод до насыщения (пока срабатывают правила).

        Args:
            strategy: Стратегия разрешения конфликтов
                      (order, specificity, recency)

        Returns:
            Список примененных правил в порядке их срабатывания
        """
        applied: List[AppliedRule] = []
        iteration = 0

        # Цикл продолжается пока есть применимые правила
        while True:
            # Формируем конфликтное множество
            conflict_set = self._collect_conflict_set()

            if not conflict_set:
                break

            # Выбираем правило согласно стратегии
            rule = self._resolve_conflict(conflict_set, strategy)

            if rule is None:
                break

            # Пытаемся применить правило
            added = self.working_memory.add_fact(
                fact=rule.conclusion,
                source=rule.id,
                supports=list(rule.conditions),
            )

            if added:
                # Правило успешно применено
                iteration += 1
                applied.append(AppliedRule(rule=rule, iteration=iteration))
            else:
                # Правило не добавило новый факт, исключаем его и продолжаем
                conflict_set.remove(rule)
                if not conflict_set:
                    break

        return applied

    def _collect_conflict_set(self) -> List[Rule]:
        """
        Формирует конфликтное множество правил.

        Конфликтное множество - это правила, у которых все условия
        выполнены, но заключение еще не выведено.

        Returns:
            Список правил, готовых к применению
        """
        conflicts: List[Rule] = []

        for rule in self._kb.rules:
            # Пропускаем правило, если его заключение уже выведено
            if self.working_memory.has_fact(rule.conclusion):
                continue

            # Проверяем, все ли условия выполнены
            if all(self.working_memory.has_fact(condition) for condition in rule.conditions):
                conflicts.append(rule)

        return conflicts

    def _resolve_conflict(
            self,
            conflicts: Sequence[Rule],
            strategy: ConflictStrategy,
    ) -> Rule | None:
        """
        Выбирает правило из конфликтного множества согласно стратегии.

        Поддерживаемые стратегии:
        - order: правила применяются в порядке объявления в БЗ
        - specificity: выбирается правило с наибольшим числом условий
        - recency: правило с наиболее свежими фактами в предпосылках

        Args:
            conflicts: Конфликтное множество правил
            strategy: Название стратегии

        Returns:
            Выбранное правило или None, если множество пусто

        Raises:
            ValueError: Если указана неизвестная стратегия
        """
        if not conflicts:
            return None

        strategy = strategy.lower()

        # Стратегия 1: По порядку объявления правил
        if strategy == "order":
            return conflicts[0]

        # Стратегия 2: По специфичности (больше условий = выше приоритет)
        if strategy == "specificity":
            return max(conflicts, key=lambda rule: len(rule.conditions))

        # Стратегия 3: По свежести фактов (максимальная временная метка)
        if strategy == "recency":
            def recency_score(rule: Rule) -> int:
                """
                Вычисляет оценку свежести правила.

                Оценка = максимальная временная метка среди условий правила.
                """
                timestamps = [
                    self.working_memory.get_record(condition).timestamp
                    for condition in rule.conditions
                ]
                return max(timestamps) if timestamps else 0

            return max(conflicts, key=recency_score)

        raise ValueError(f"Неизвестная стратегия разрешения конфликтов: {strategy}")

    # --- НОВЫЙ МЕТОД ДЛЯ ЛАБЫ №3 ---
    def build_frames_from_rules(self) -> None:
        """
        Переводит правила из JSON в фреймы.
        Каждое правило-результат становится фреймом-факультетом,
        а условия - слотами-требованиями.
        """
        for rule in self._kb.rules:
            # Берём только правила, которые выдают "Результат = ..."
            if rule.conclusion.startswith("Результат = "):
                faculty_name = rule.conclusion.replace("Результат = ", "")

                if faculty_name not in self.working_memory.frames:
                    frame = Frame(faculty_name)

                    # Навешиваем условия как слоты фрейма
                    for cond in rule.conditions:
                        cond_clean = cond.replace(" = да", "").replace("Специализация = ", "специализация_")
                        frame.set_slot_value(cond_clean, "да")

                    self.working_memory.add_frame(frame)