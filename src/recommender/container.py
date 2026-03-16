from dependency_injector import containers, providers

from src.recommender.config import Settings
from src.recommender.repository import ContentRepository
from src.recommender.service import RecommendationService


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)

    repository = providers.Singleton(
        ContentRepository,
        data_dir=config.provided.data_dir,
        movies_csv=config.provided.movies_csv,
        tv_csv=config.provided.tv_csv,
    )

    recommendation_service = providers.Singleton(
        RecommendationService,
        repo=repository,
        default_limit=config.provided.default_limit,
    )
