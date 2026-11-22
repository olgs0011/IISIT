"""
Модуль, реализующий компонент объяснения для фреймовой системы Минского
"""
from typing import List, Dict, Any
from inference_engine import InferenceEngine


class ExplanationComponent:
    """Компонента объяснения для фреймовой системы Минского"""

    def __init__(self, inference_engine: InferenceEngine):
        self.ie = inference_engine

    def explain_recommendation(self, faculty_name: str) -> str:
        """Объясняет, почему данный факультет был рекомендован"""
        # Находим соответствующий протофрейм
        proto_frames = self.ie.working_memory.get_proto_frames()
        target_proto = None

        for proto in proto_frames:
            ako_frame = proto.slots["AKO"].value
            if ako_frame and ako_frame.name == faculty_name:
                target_proto = proto
                break

        if not target_proto:
            return f"Факультет '{faculty_name}' не найден среди рекомендаций"

        # Получаем объяснение через IF-NEEDED процедуру
        reason_slot = target_proto.get_slot("причина_рекомендации")
        if reason_slot:
            reason = target_proto.get_slot_value("причина_рекомендации")
        else:
            # Ручное объяснение
            reasons = []
            requires_algo = target_proto.get_slot_value("требует_алгоритмическое_мышление")
            if requires_algo == "да":
                reasons.append("Требуется алгоритмическое мышление")
            requires_analit = target_proto.get_slot_value("требует_аналитическое_мышление")
            if requires_analit == "да":
                reasons.append("Требуется аналитическое мышление")
            requires_creative = target_proto.get_slot_value("требует_творческое_мышление")
            if requires_creative == "да":
                reasons.append("Требуется творческое мышление")
            requires_finance = target_proto.get_slot_value("требует_финансовую_грамотность")
            if requires_finance == "да":
                reasons.append("Требуется финансовая грамотность")
            reason = "; ".join(reasons) if reasons else "Общие характеристики совпадают"

        # Получаем предпочтения пользователя
        preferences = self.ie.working_memory.get_preferences()

        explanation = f"Факультет '{faculty_name}' рекомендован по следующим причинам:\n"
        explanation += f"  - {reason}\n\n"

        explanation += "Ваши характеристики:\n"
        if preferences.get("Алгоритмическое мышление", "нет") != "нет":
            explanation += f"  - Алгоритмическое мышление: {preferences.get('Алгоритмическое мышление')}\n"
        if preferences.get("Аналитическое мышление", "нет") != "нет":
            explanation += f"  - Аналитическое мышление: {preferences.get('Аналитическое мышление')}\n"
        if preferences.get("Творческое мышление", "нет") != "нет":
            explanation += f"  - Творческое мышление: {preferences.get('Творческое мышление')}\n"
        if preferences.get("Финансовая грамотность", "нет") != "нет":
            explanation += f"  - Финансовая грамотность: {preferences.get('Финансовая грамотность')}\n"

        specializations = preferences.get("Специализации", [])
        if specializations:
            explanation += f"\nПодходящие специализации: {', '.join(specializations)}\n"

        return explanation

    def get_inference_trace(self) -> List[Dict[str, Any]]:
        """Возвращает историю вывода"""
        return self.ie.working_memory.get_trace()

