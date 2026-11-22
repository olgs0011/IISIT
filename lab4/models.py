from collections import defaultdict, Counter
from itertools import combinations


def relative_majority(profile: list[list[str]], alternatives: list[str]) -> tuple[str, dict[str, int]]:
    """Относительное большинство: побеждает тот, кто чаще стоит на 1-м месте."""
    first_choices = [ranking[0] for ranking in profile]
    counts = Counter(first_choices)
    winner = max(counts, key=counts.get)
    return winner, dict(counts)


def pairwise_comparison(profile: list[list[str]], a: str, b: str) -> int:
    """Возвращает разность: сколько предпочитают a над b минус наоборот."""
    score = 0
    for ranking in profile:
        if a in ranking and b in ranking:
            if ranking.index(a) < ranking.index(b):
                score += 1
            else:
                score -= 1
    return score


def condorcet_winner(profile: list[list[str]], alternatives: list[str]) -> str | None:
    """Явный победитель Кондорсе: побеждает всех в попарных сравнениях."""
    for a in alternatives:
        is_winner = True
        for b in alternatives:
            if a == b:
                continue
            if pairwise_comparison(profile, a, b) <= 0:
                is_winner = False
                break
        if is_winner:
            return a
    return None


def copeland_score(profile: list[list[str]], alternatives: list[str]) -> dict[str, int]:
    """Правило Копленда: +1 за победу, -1 за поражение, 0 за ничью."""
    scores = {a: 0 for a in alternatives}
    for a, b in combinations(alternatives, 2):
        diff = pairwise_comparison(profile, a, b)
        if diff > 0:
            scores[a] += 1
            scores[b] -= 1
        elif diff < 0:
            scores[a] -= 1
            scores[b] += 1
        # ничья: ничего не добавляем
    return scores


def simpson_score(profile: list[list[str]], alternatives: list[str]) -> dict[str, int]:
    """Правило Симпсона: минимальное число голосов, с которым кандидат побеждает любого другого."""
    scores = {}
    for a in alternatives:
        min_wins = float('inf')
        for b in alternatives:
            if a == b:
                continue
            wins = sum(1 for ranking in profile if ranking.index(a) < ranking.index(b))
            min_wins = min(min_wins, wins)
        scores[a] = min_wins if min_wins != float('inf') else 0
    return scores


def borda_count(profile: list[list[str]], alternatives: list[str]) -> dict[str, int]:
    """Модель Борда: p-1 очков за 1-е место, ..., 0 за последнее."""
    p = len(alternatives)
    scores = defaultdict(int)
    for ranking in profile:
        for i, alt in enumerate(ranking):
            scores[alt] += (p - 1 - i)
    # Убедимся, что все альтернативы присутствуют
    for alt in alternatives:
        scores.setdefault(alt, 0)
    return dict(scores)


# Формируем объяснения
def generate_explanations(profile, alternatives, results):
    """
    Формирует текстовые объяснения для каждого метода.
    Возвращает словарь: {метод: "текст объяснения"}
    """
    explanations = {}
    total_voters = len(profile)

    # 1. Относительное большинство
    winner_maj = results["relative_majority"]["winner"]
    counts = results["relative_majority"]["counts"]

    if winner_maj.startswith("Ничья:"):
        explanations["relative_majority"] = (
            f"По правилу относительного большинства определилась ничья. "
            f"Несколько вариантов набрали одинаковое максимальное количество первых мест."
        )
    else:
        max_votes = counts.get(winner_maj, 0)
        explanations["relative_majority"] = (
            f"Вариант «{winner_maj}» победил, потому что его поставили на первое место "
            f"{max_votes} из {total_voters} избирателей. Это относительное большинство: "
            f"он набрал больше первых мест, чем любой другой вариант."
        )

    # 2. Кондорсе
    cond = results["condorcet_winner"]
    if cond:
        explanations["condorcet"] = (
            f"Вариант «{cond}» является победителем Кондорсе, потому что при попарном сравнении "
            f"он побеждает каждый из остальных вариантов. То есть большинство избирателей "
            f"предпочитает его любому другому варианту."
        )
    else:
        explanations["condorcet"] = (
            "Явного победителя Кондорсе нет. Это означает, что в голосовании возник "
            "парадокс Кондорсе: предпочтения избирателей циклические (например, A лучше B, "
            "B лучше C, но C лучше A). Такой вариант невозможен при выборе из двух вариантов, "
            "но возможен при трёх и более."
        )

    # 3. Копленд
    cop_scores = results["copeland_scores"]
    cop_winner = results["copeland_winner"]

    if cop_winner.startswith("Ничья:"):
        explanations["copeland"] = (
            f"По правилу Копленда определилась ничья. Несколько вариантов набрали одинаковое "
            f"максимальное количество очков при попарном сравнении."
        )
    else:
        explanations["copeland"] = (
            f"Вариант «{cop_winner}» победил по правилу Копленда: он набрал {cop_scores[cop_winner]} "
            f"очков (за каждую победу над другим вариантом в попарном сравнении +1, за поражение -1). "
            f"Это максимальный результат среди всех вариантов."
        )

    # 4. Симпсон
    sim_scores = results["simpson_scores"]
    sim_winner = results["simpson_winner"]

    if sim_winner.startswith("Ничья:"):
        explanations["simpson"] = (
            f"По правилу Симпсона определилась ничья. Несколько вариантов имеют одинаковую "
            f"минимальную поддержку при попарных сравнениях."
        )
    else:
        explanations["simpson"] = (
            f"Вариант «{sim_winner}» победил по правилу Симпсона: его минимальная поддержка "
            f"при сравнении с любым другим вариантом составляет {sim_scores[sim_winner]} голосов. "
            f"Это значит, что даже в самом неудобном для него попарном сравнении он сохраняет "
            f"поддержку большинства."
        )

    # 5. Борда
    bor_scores = results["borda_scores"]
    bor_winner = results["borda_winner"]

    if bor_winner.startswith("Ничья:"):
        explanations["borda"] = (
            f"По модели Борда определилась ничья. Несколько вариантов набрали одинаковое "
            f"суммарное количество очков за свои позиции."
        )
    else:
        explanations["borda"] = (
            f"Вариант «{bor_winner}» победил по модели Борда: он набрал {bor_scores[bor_winner]} очков. "
            f"Очки начисляются за позицию: за 1-е место — максимум, за последнее — 0. "
            f"Победа означает, что этот вариант в среднем стоит выше остальных у большинства избирателей."
        )

    return explanations