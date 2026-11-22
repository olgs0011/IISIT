from typing import List

from working_memory import WorkingMemory


class ExplanationComponent:
    """
    Компонента объяснения для построения цепочек логического вывода.

    Формирует текстовое объяснение происхождения факта,
    рекурсивно раскрывая цепочку правил и фактов-предпосылок.
    """

    def __init__(self, working_memory: WorkingMemory) -> None:
        """
        Инициализирует компоненту объяснения.

        Args:
            working_memory: Рабочая память с фактами
        """
        self._wm = working_memory

    def explain(self, fact: str) -> str:
        """
        Возвращает текстовое объяснение происхождения факта.

        Args:
            fact: Факт, для которого нужно построить объяснение

        Returns:
            Многострочное текстовое объяснение

        Raises:
            ValueError: Если факт отсутствует в рабочей памяти
        """
        if not self._wm.has_fact(fact):
            raise ValueError(f"Факт '{fact}' отсутствует в рабочей памяти.")

        lines: List[str] = []
        self._build_explanation(fact, lines, depth=0)
        return "\n".join(lines)

    def _build_explanation(self, fact: str, lines: List[str], depth: int) -> None:
        """
        Рекурсивно строит объяснение для факта.

        Args:
            fact: Факт для объяснения
            lines: Список строк для накопления результата
            depth: Глубина вложенности (для отступов)
        """
        record = self._wm.get_record(fact)
        indent = "  " * depth

        # Базовый случай: факт введен пользователем
        if record.source == "user":
            lines.append(f"{indent}- Факт '{fact}' введён пользователем.")
            return

        # Рекурсивный случай: факт выведен правилом
        lines.append(f"{indent}- Факт '{fact}' получен по правилу {record.source}.")

        if not record.supports:
            return

        # Рекурсивно объясняем факты-предпосылки
        lines.append(f"{indent}  Обоснование:")
        for support in record.supports:
            self._build_explanation(support, lines, depth + 2)


