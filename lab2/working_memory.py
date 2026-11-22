from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class FactRecord:
    """
    Запись о факте в рабочей памяти.

    Attributes:
        fact: Текст факта
        source: Источник факта (user или ID правила)
        supports: Список фактов, поддерживающих данный факт
        timestamp: Временная метка добавления факта
    """
    fact: str
    source: str
    supports: List[str]
    timestamp: int


class WorkingMemory:
    """
    Рабочая память экспертной системы.

    Хранит факты в виде записей с метаданными и обеспечивает
    доступ к фактам для механизма вывода и компоненты объяснения.
    """

    def __init__(self) -> None:
        """Инициализирует пустую рабочую память."""
        self._facts: Dict[str, FactRecord] = {}
        self._counter: int = 0

    def add_fact(
            self,
            fact: str,
            source: str,
            supports: Optional[Iterable[str]] = None
    ) -> bool:
        """
        Добавляет новый факт в рабочую память.

        Args:
            fact: Текст факта для добавления
            source: Источник факта (user или ID правила)
            supports: Список фактов-предпосылок (необязательно)

        Returns:
            True, если факт был добавлен впервые
            False, если факт уже присутствовал в памяти
        """
        if fact in self._facts:
            return False

        self._counter += 1
        record = FactRecord(
            fact=fact,
            source=source,
            supports=list(supports or []),
            timestamp=self._counter,
        )
        self._facts[fact] = record
        return True

    def has_fact(self, fact: str) -> bool:
        """
        Проверяет наличие факта в рабочей памяти.

        Args:
            fact: Текст факта для проверки

        Returns:
            True, если факт присутствует в памяти
        """
        return fact in self._facts

    def get_record(self, fact: str) -> FactRecord:
        """
        Возвращает запись о факте с метаданными.

        Args:
            fact: Текст факта

        Returns:
            Запись с метаданными факта

        Raises:
            KeyError: Если факт не найден в памяти
        """
        return self._facts[fact]

    def facts(self) -> List[str]:
        """
        Возвращает список всех фактов в порядке их добавления.

        Returns:
            Список текстов фактов, упорядоченный по времени добавления
        """
        return [
            record.fact
            for record in sorted(self._facts.values(), key=lambda item: item.timestamp)
        ]

    def items(self) -> List[FactRecord]:
        """
        Возвращает все записи фактов в порядке добавления.

        Returns:
            Список записей фактов с метаданными
        """
        return list(sorted(self._facts.values(), key=lambda item: item.timestamp))
