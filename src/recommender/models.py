from typing import List, Optional
from pydantic import BaseModel, Field


class BaseRequest(BaseModel):
    user_id: str = Field(..., examples=["A"])
    is_movie: bool = Field(True, description="True for movies, False for TV shows")
    limit: Optional[int] = Field(None, ge=1, le=100, examples=[10])
    min_popularity: Optional[float] = Field(None, ge=0, examples=[50])
    min_rating: Optional[float] = Field(None, ge=0, le=10, examples=[6.5])


class GenresRequest(BaseRequest):
    current_genres: List[str] = Field(..., examples=[["Action", "Adventure"]])


class CountryRequest(BaseRequest):
    last_watch_country: str = Field(..., examples=["United States of America"])


class TitleRequest(BaseRequest):
    last_watch_title: str = Field(..., examples=["Iron man"])


class CastRequest(BaseRequest):
    last_watch_cast: str = Field(..., examples=["Leonardo DiCaprio"])


class DirectorRequest(BaseRequest):
    last_watch_director: str = Field(..., examples=["Christopher Nolan"])


class DescriptionRequest(BaseRequest):
    last_watch_title: str = Field(..., examples=["Inception"])


class RecommendationItem(BaseModel):
    show_id: str
    type: str
    title: str
    director: str
    cast: str
    country: str
    date_added: str
    release_year: int
    rating: Optional[float] = None
    duration: str
    genres: str
    language: str
    description: str
    popularity: Optional[float] = None
    vote_count: Optional[float] = None
    vote_average: Optional[float] = None
    budget: Optional[float] = None
    revenue: Optional[float] = None
    score: Optional[float] = None


class RecommendationResponse(BaseModel):
    user_id: str
    count: int
    results: List[RecommendationItem]
