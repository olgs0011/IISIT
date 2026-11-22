import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


@dataclass(frozen=True)
class Rule:
    """
    Продукционное правило экспертной системы.
    Правило имеет вид: ЕСЛИ <условия> ТО <заключение>
    Attributes:
        id: Уникальный идентификатор правила
        conditions: Список условий (фактов-предпосылок)
        conclusion: Заключение (выводимый факт)
    """
    id: str
    conditions: Sequence[str]
    conclusion: str


class KnowledgeBase:
    """
    База знаний экспертной системы.

    Содержит упорядоченный набор продукционных правил,
    загружаемых из JSON-файла.
    """

    def __init__(self, rules: Sequence[Rule]) -> None:
        """
        Инициализирует базу знаний.

        Args:
            rules: Последовательность правил

        Raises:
            ValueError: Если список правил пуст
        """
        if not rules:
            raise ValueError("База знаний не может быть пустой.")
        self._rules: List[Rule] = list(rules)

    @property
    def rules(self) -> Sequence[Rule]:
        """
        Возвращает правила в исходном порядке.

        Returns:
            Кортеж правил
        """
        return tuple(self._rules)

    @classmethod
    def from_json(cls, path: Path) -> "KnowledgeBase":
        """
        Загружает правила из JSON-файла.

        Формат JSON-файла:
        {
            "rules": [
                {
                    "id": "R1",
                    "conditions": ["условие1", "условие2"],
                    "conclusion": "заключение"
                },
                ...
            ]
        }

        Args:
            path: Путь к JSON-файлу с правилами

        Returns:
            Экземпляр базы знаний с загруженными правилами

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если формат файла некорректен
        """
        if not path.exists():
            raise FileNotFoundError(f"Файл с правилами не найден: {path}")

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        raw_rules = payload.get("rules")
        if not isinstance(raw_rules, list):
            raise ValueError("Некорректный формат файла правил: отсутствует список 'rules'.")

        rules: List[Rule] = []
        for item in raw_rules:
            try:
                rule = Rule(
                    id=str(item["id"]),
                    conditions=tuple(item["conditions"]),
                    conclusion=str(item["conclusion"]),
                )
            except (KeyError, TypeError) as error:
                raise ValueError(f"Ошибка парсинга правила: {item}") from error
            rules.append(rule)

        return cls(rules)


