from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from models import (
    relative_majority,
    condorcet_winner,
    copeland_score,
    simpson_score,
    borda_count,
    generate_explanations
)

app = FastAPI(title="Система коллективного принятия решений")
# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модели данных для API
class CalculateResultsRequest(BaseModel):
    profile: List[List[str]]
    alternatives: List[str]


class ResultsResponse(BaseModel):
    relative_majority: dict
    condorcet_winner: Optional[str]
    copeland_scores: dict
    copeland_winner: str
    simpson_scores: dict
    simpson_winner: str
    borda_scores: dict
    borda_winner: str
    explanations: dict


# Раздача статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    """Главная страница - возвращает HTML файл"""
    return FileResponse("static/index.html")


@app.post("/api/calculate", response_model=ResultsResponse)
async def calculate_results(request: CalculateResultsRequest):
    """
        Вычисляет результаты голосования по различным методам.
        Args:
            request: Запрос с профилем голосования и альтернативами
        Returns:
            Результаты вычислений по всем методам
        """
    try:
        profile = request.profile
        alternatives = request.alternatives
        # Валидация данных
        if not profile:
            raise HTTPException(status_code=400, detail="Профиль голосования не может быть пустым")
        if not alternatives:
            raise HTTPException(status_code=400, detail="Список альтернатив не может быть пустым")
        # Проверка, что все альтернативы присутствуют в профиле
        all_profile_items = set()
        for ranking in profile:
            all_profile_items.update(ranking)

        if not all_profile_items.issubset(set(alternatives)):
            raise HTTPException(
                status_code=400,
                detail="Профиль содержит альтернативы, которых нет в списке альтернатив"
            )

        # Вычисление результатов
        # Вспомогательная функция для поиска победителя или ничьей
        def get_winner(scores_dict):
            max_score = max(scores_dict.values())
            winners = [k for k, v in scores_dict.items() if v == max_score]
            if len(winners) > 1:
                return "Ничья: " + ", ".join(winners)
            return winners[0]

        # 1. Относительное большинство
        maj_winner, maj_counts = relative_majority(profile, alternatives)
        max_votes = max(maj_counts.values())
        maj_winners = [k for k, v in maj_counts.items() if v == max_votes]
        if len(maj_winners) > 1:
            maj_winner = "Ничья: " + ", ".join(maj_winners)

        # 2. Кондорсе
        cond_winner = condorcet_winner(profile, alternatives)

        # 3. Копленд
        cop_scores = copeland_score(profile, alternatives)
        cop_winner = get_winner(cop_scores)

        # 4. Симпсон
        sim_scores = simpson_score(profile, alternatives)
        sim_winner = get_winner(sim_scores)

        # 5. Борда
        bor_scores = borda_count(profile, alternatives)
        bor_winner = get_winner(bor_scores)

        # Собираем результаты для объяснений
        results_for_expl = {
            "relative_majority": {"winner": maj_winner, "counts": maj_counts},
            "condorcet_winner": cond_winner,
            "copeland_scores": cop_scores,
            "copeland_winner": cop_winner,
            "simpson_scores": sim_scores,
            "simpson_winner": sim_winner,
            "borda_scores": bor_scores,
            "borda_winner": bor_winner,
        }
        explanations = generate_explanations(profile, alternatives, results_for_expl)

        return ResultsResponse(
            relative_majority={
                "winner": maj_winner,
                "counts": maj_counts
            },
            condorcet_winner=cond_winner,
            copeland_scores=cop_scores,
            copeland_winner=cop_winner,
            simpson_scores=sim_scores,
            simpson_winner=sim_winner,
            borda_scores=bor_scores,
            borda_winner=bor_winner,
            explanations=explanations
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при вычислении результатов: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)