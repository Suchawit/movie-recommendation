from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


class ContentRepository:
    def __init__(self, data_dir: str, movies_csv: str, tv_csv: str) -> None:
        base = Path(data_dir)
        self._frames: Dict[str, pd.DataFrame] = {}
        self._frames["Movie"] = self._load_csv(base / movies_csv, "Movie")
        self._frames["TV Show"] = self._load_csv(base / tv_csv, "TV Show")

    @staticmethod
    def _load_csv(path: Path, content_type: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        df["type"] = content_type

        for col in [
            "show_id",
            "type",
            "title",
            "director",
            "cast",
            "country",
            "date_added",
            "duration",
            "genres",
            "language",
            "description",
        ]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)

        for col in [
            "release_year",
            "rating",
            "popularity",
            "vote_count",
            "vote_average",
            "budget",
            "revenue",
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df["date_added_dt"] = pd.to_datetime(df["date_added"], errors="coerce")

        df["title_lc"] = df["title"].str.lower()
        df["genres_lc"] = df["genres"].str.lower()
        df["cast_lc"] = df["cast"].str.lower()
        df["director_lc"] = df["director"].str.lower()
        df["country_lc"] = df["country"].str.lower()
        df["description_lc"] = df["description"].str.lower()

        return df

    def get_frame(self, is_movie: bool) -> pd.DataFrame:
        return self._frames["Movie" if is_movie else "TV Show"].copy()
