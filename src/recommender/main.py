import logging
from fastapi import Depends, FastAPI

from src.recommender.container import Container
from src.recommender.models import (
    CastRequest,
    CountryRequest,
    DescriptionRequest,
    DirectorRequest,
    GenresRequest,
    RecommendationResponse,
    TitleRequest,
)
from src.recommender.service import RecommendationParams, RecommendationService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("recommender")

container = Container()
app = FastAPI(
    title="Movie & TV Recommendation API",
    version="1.0.0",
    description="Rule-based content recommendation over Netflix movies and TV shows.",
)

app.container = container


def _to_params(req) -> RecommendationParams:
    return RecommendationParams(
        user_id=req.user_id,
        is_movie=req.is_movie,
        limit=req.limit or container.config().default_limit,
        min_popularity=req.min_popularity,
        min_rating=req.min_rating,
    )


def _get_service() -> RecommendationService:
    return container.recommendation_service()


@app.get("/health")
async def health() -> dict:
    logger.info("health check")
    return {"status": "ok"}

@app.post("/recommend/genres", response_model=RecommendationResponse)
async def recommend_genres(
    req: GenresRequest,
    service: RecommendationService = Depends(_get_service),
) -> RecommendationResponse:
    params = _to_params(req)
    return await service.recommend_by_genres(params, req.current_genres)


@app.post("/recommend/country", response_model=RecommendationResponse)
async def recommend_country(
    req: CountryRequest,
    service: RecommendationService = Depends(_get_service),
) -> RecommendationResponse:
    params = _to_params(req)
    return await service.recommend_by_country(params, req.last_watch_country)


@app.post("/recommend/title", response_model=RecommendationResponse)
async def recommend_title(
    req: TitleRequest,
    service: RecommendationService = Depends(_get_service),
) -> RecommendationResponse:
    params = _to_params(req)
    return await service.recommend_by_title(params, req.last_watch_title)


@app.post("/recommend/cast", response_model=RecommendationResponse)
async def recommend_cast(
    req: CastRequest,
    service: RecommendationService = Depends(_get_service),
) -> RecommendationResponse:
    params = _to_params(req)
    return await service.recommend_by_cast(params, req.last_watch_cast)


@app.post("/recommend/director", response_model=RecommendationResponse)
async def recommend_director(
    req: DirectorRequest,
    service: RecommendationService = Depends(_get_service),
) -> RecommendationResponse:
    params = _to_params(req)
    return await service.recommend_by_director(params, req.last_watch_director)


@app.post("/recommend/description", response_model=RecommendationResponse)
async def recommend_description(
    req: DescriptionRequest,
    service: RecommendationService = Depends(_get_service),
) -> RecommendationResponse:
    params = _to_params(req)
    return await service.recommend_by_description(params, req.last_watch_title)
