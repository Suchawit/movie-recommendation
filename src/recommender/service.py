from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List, Optional

import pandas as pd

from src.recommender.models import RecommendationItem, RecommendationResponse
from src.recommender.repository import ContentRepository


@dataclass
class RecommendationParams:
    user_id: str
    is_movie: bool
    limit: int
    min_popularity: Optional[float]
    min_rating: Optional[float]


class RecommendationService:
    def __init__(self, repo: ContentRepository, default_limit: int) -> None:
        self._repo = repo
        self._default_limit = default_limit

    def recommend_by_genres(
        self, params: RecommendationParams, current_genres: List[str]
    ) -> RecommendationResponse:
        frame = self._repo.get_frame(params.is_movie)
        terms = [g.strip().lower() for g in current_genres if g.strip()]
        if terms:
            mask = frame["genres_lc"].apply(lambda g: any(t in g for t in terms))
            frame = frame[mask]
        frame = self._apply_min_filters(frame, params)
        frame["score"] = frame["genres_lc"].apply(
            lambda g: sum(1 for t in terms if t in g) if terms else 0
        )
        return self._build_response(params.user_id, frame, params.limit)

    def recommend_by_country(
        self, params: RecommendationParams, last_watch_country: str
    ) -> RecommendationResponse:
        frame = self._repo.get_frame(params.is_movie)
        country = last_watch_country.strip().lower()
        if country:
            frame = frame[frame["country_lc"].str.contains(country, na=False)]
        frame = self._apply_min_filters(frame, params)
        frame["score"] = frame["popularity"].fillna(0)
        return self._build_response(params.user_id, frame, params.limit)

    def recommend_by_title(
        self, params: RecommendationParams, last_watch_title: str
    ) -> RecommendationResponse:
        frame = self._repo.get_frame(params.is_movie)
        title = last_watch_title.strip()
        if title:
            title_norm = self._normalize_title(title)
            base = self._base_title(title_norm)
            exact = frame[frame["title_lc"] == title_norm]
            if not exact.empty:
                seed_genres = exact.iloc[0]["genres_lc"]
                frame["score"] = frame["genres_lc"].apply(
                    lambda g: self._token_overlap(seed_genres, g)
                )
            else:
                frame["score"] = frame["title_lc"].apply(
                    lambda t: self._token_overlap(title_norm, t)
                )
            if base:
                base_mask = frame["title_lc"].str.contains(
                    re.escape(base), case=False, na=False
                )
                base_scores = frame.loc[base_mask, "score"].fillna(0)
                frame.loc[base_mask, "score"] = base_scores + frame.loc[base_mask, "title_lc"].apply(
                    lambda t: self._sequel_boost(t, title_norm, base)
                )
        else:
            frame["score"] = 0
        frame = frame[frame["score"] > 0]
        filtered = self._apply_min_filters(frame, params)
        if filtered.empty and title:
            frame = frame
        else:
            frame = filtered
        return self._build_response(params.user_id, frame, params.limit)

    def recommend_by_cast(
        self, params: RecommendationParams, last_watch_cast: str
    ) -> RecommendationResponse:
        frame = self._repo.get_frame(params.is_movie)
        cast = last_watch_cast.strip().lower()
        if cast:
            frame["score"] = frame["cast_lc"].apply(
                lambda c: 1.0 if cast in c else self._token_overlap(cast, c)
            )
            frame = frame[frame["score"] > 0]
        frame = self._apply_min_filters(frame, params)
        return self._build_response(params.user_id, frame, params.limit)

    def recommend_by_director(
        self, params: RecommendationParams, last_watch_director: str
    ) -> RecommendationResponse:
        frame = self._repo.get_frame(params.is_movie)
        director = last_watch_director.strip().lower()
        if director:
            frame["score"] = frame["director_lc"].apply(
                lambda d: 1.0 if director in d else self._token_overlap(director, d)
            )
            frame = frame[frame["score"] > 0]
        frame = self._apply_min_filters(frame, params)
        return self._build_response(params.user_id, frame, params.limit)

    def recommend_by_description(
        self, params: RecommendationParams, last_watch_title: str
    ) -> RecommendationResponse:
        frame = self._repo.get_frame(params.is_movie)
        title = last_watch_title.strip().lower()
        seed_desc = ""
        if title:
            match = frame[frame["title_lc"].str.contains(title, na=False)]
            if not match.empty:
                seed_desc = match.iloc[0]["description_lc"]
        if seed_desc:
            frame["score"] = frame["description_lc"].apply(
                lambda d: self._token_overlap(seed_desc, d)
            )
            frame = frame[frame["score"] > 0]
        frame = self._apply_min_filters(frame, params)
        return self._build_response(params.user_id, frame, params.limit)

    def _apply_min_filters(
        self, frame: pd.DataFrame, params: RecommendationParams
    ) -> pd.DataFrame:
        if params.min_popularity is not None:
            frame = frame[frame["popularity"] >= params.min_popularity]
        if params.min_rating is not None:
            frame = frame[frame["vote_average"] >= params.min_rating]
        return frame

    def _build_response(
        self, user_id: str, frame: pd.DataFrame, limit: int
    ) -> RecommendationResponse:
        limit = limit or self._default_limit
        if "score" not in frame.columns:
            frame["score"] = 0
        frame = frame.sort_values(
            by=["score", "date_added_dt", "popularity", "vote_average"],
            ascending=[False, False, False, False],
            na_position="last",
        )
        if len(frame) > limit:
            frame = frame.head(limit)
        items = [self._row_to_item(row) for _, row in frame.iterrows()]
        return RecommendationResponse(user_id=user_id, count=len(items), results=items)

    @staticmethod
    def _token_overlap(a: str, b: str) -> float:
        a_tokens = {t for t in a.replace(",", " ").split() if len(t) > 2}
        b_tokens = {t for t in b.replace(",", " ").split() if len(t) > 2}
        if not a_tokens or not b_tokens:
            return 0.0
        return len(a_tokens & b_tokens) / len(a_tokens)

    @staticmethod
    def _normalize_title(title: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", title.lower())
        return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def _base_title(title: str) -> str:
        sequel_tokens = {
            "part",
            "episode",
            "season",
            "chapter",
            "vol",
            "volume",
        }
        roman = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"}
        tokens = []
        for token in title.split():
            if token in sequel_tokens:
                continue
            if token.isdigit() or token in roman:
                continue
            tokens.append(token)
        return " ".join(tokens).strip()

    @staticmethod
    def _sequel_boost(title_lc: str, exact_title_lc: str, base: str) -> float:
        if not base:
            return 0.0
        if title_lc == exact_title_lc:
            return 0.5
        sequel_pattern = re.compile(
            r"\b(2|3|4|5|6|7|8|9|10|ii|iii|iv|v|vi|vii|viii|ix|x|season|episode|chapter|part)\b",
            re.IGNORECASE,
        )
        if sequel_pattern.search(title_lc):
            return 3.0
        return 1.5

    @staticmethod
    def _row_to_item(row: pd.Series) -> RecommendationItem:
        return RecommendationItem(
            show_id=str(row.get("show_id", "")),
            type=row.get("type", ""),
            title=row.get("title", ""),
            director=row.get("director", ""),
            cast=row.get("cast", ""),
            country=row.get("country", ""),
            date_added=str(row.get("date_added", "")),
            release_year=int(row.get("release_year"))
            if pd.notna(row.get("release_year"))
            else 0,
            rating=float(row.get("rating"))
            if pd.notna(row.get("rating"))
            else None,
            duration=row.get("duration", ""),
            genres=row.get("genres", ""),
            language=row.get("language", ""),
            description=row.get("description", ""),
            popularity=float(row.get("popularity"))
            if pd.notna(row.get("popularity"))
            else None,
            vote_count=float(row.get("vote_count"))
            if pd.notna(row.get("vote_count"))
            else None,
            vote_average=float(row.get("vote_average"))
            if pd.notna(row.get("vote_average"))
            else None,
            budget=float(row.get("budget"))
            if pd.notna(row.get("budget"))
            else None,
            revenue=float(row.get("revenue"))
            if pd.notna(row.get("revenue"))
            else None,
            score=float(row.get("score")) if pd.notna(row.get("score")) else None,
        )
