import unittest

import pandas as pd

from recommender.service import RecommendationParams, RecommendationService


class FakeRepo:
    def __init__(self, frame: pd.DataFrame) -> None:
        self.frame = frame

    async def get_frame(self, is_movie: bool) -> pd.DataFrame:
        return self.frame.copy()


def _sample_frame() -> pd.DataFrame:
    data = [
        {
            "show_id": "1",
            "type": "Movie",
            "title": "Space Adventure",
            "director": "Jane Doe",
            "cast": "Actor A, Actor B",
            "country": "United States of America",
            "date_added": "2020-01-01",
            "release_year": 2020,
            "rating": 7.5,
            "duration": "100 min",
            "genres": "Action, Adventure",
            "language": "en",
            "description": "A heroic journey in space.",
            "popularity": 50.0,
            "vote_count": 1000,
            "vote_average": 7.5,
            "budget": 1000000,
            "revenue": 3000000,
        },
        {
            "show_id": "2",
            "type": "Movie",
            "title": "Romantic Escape",
            "director": "John Smith",
            "cast": "Actor C",
            "country": "France",
            "date_added": "2021-01-01",
            "release_year": 2021,
            "rating": 6.0,
            "duration": "95 min",
            "genres": "Romance, Drama",
            "language": "fr",
            "description": "A love story.",
            "popularity": 30.0,
            "vote_count": 500,
            "vote_average": 6.0,
            "budget": 500000,
            "revenue": 1500000,
        },
        {
            "show_id": "3",
            "type": "Movie",
            "title": "Space Adventure 2",
            "director": "Jane Doe",
            "cast": "Actor A, Actor D",
            "country": "United States of America",
            "date_added": "2022-01-01",
            "release_year": 2022,
            "rating": 7.9,
            "duration": "105 min",
            "genres": "Action, Adventure",
            "language": "en",
            "description": "The journey continues.",
            "popularity": 70.0,
            "vote_count": 2000,
            "vote_average": 7.9,
            "budget": 2000000,
            "revenue": 5000000,
        },
    ]
    df = pd.DataFrame(data)
    df["date_added_dt"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["title_lc"] = df["title"].str.lower()
    df["genres_lc"] = df["genres"].str.lower()
    df["cast_lc"] = df["cast"].str.lower()
    df["director_lc"] = df["director"].str.lower()
    df["country_lc"] = df["country"].str.lower()
    df["description_lc"] = df["description"].str.lower()
    return df


class RecommendationServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.repo = FakeRepo(_sample_frame())
        self.service = RecommendationService(self.repo, default_limit=10)
        self.params = RecommendationParams(
            user_id="A", is_movie=True, limit=5, min_popularity=None, min_rating=None
        )

    async def test_recommend_by_genres(self) -> None:
        resp = await self.service.recommend_by_genres(self.params, ["Action"])
        self.assertGreater(resp.count, 0)
        titles = [item.title for item in resp.results]
        self.assertIn("Space Adventure", titles)

    async def test_recommend_by_cast(self) -> None:
        resp = await self.service.recommend_by_cast(self.params, "Actor C")
        titles = [item.title for item in resp.results]
        self.assertIn("Romantic Escape", titles)

    async def test_recommend_by_country(self) -> None:
        resp = await self.service.recommend_by_country(self.params, "France")
        self.assertEqual(resp.count, 1)
        self.assertEqual(resp.results[0].title, "Romantic Escape")

    async def test_recommend_by_director(self) -> None:
        resp = await self.service.recommend_by_director(self.params, "Jane Doe")
        self.assertGreaterEqual(resp.count, 1)

    async def test_recommend_by_description(self) -> None:
        resp = await self.service.recommend_by_description(
            self.params, "Space Adventure"
        )
        self.assertGreater(resp.count, 0)
        self.assertEqual(resp.results[0].title, "Space Adventure")

    async def test_recommend_by_title_sequel(self) -> None:
        resp = await self.service.recommend_by_title(self.params, "Space Adventure")
        titles = [item.title for item in resp.results]
        self.assertIn("Space Adventure 2", titles)

    async def test_min_filters(self) -> None:
        params = RecommendationParams(
            user_id="A",
            is_movie=True,
            limit=5,
            min_popularity=40,
            min_rating=7.0,
        )
        resp = await self.service.recommend_by_genres(
            params, ["Action", "Adventure"]
        )
        self.assertEqual(resp.count, 2)
        titles = [item.title for item in resp.results]
        self.assertIn("Space Adventure", titles)
        self.assertIn("Space Adventure 2", titles)

    async def test_token_overlap(self) -> None:
        overlap = self.service._token_overlap("heroic journey", "heroic space journey")
        self.assertGreater(overlap, 0)


if __name__ == "__main__":
    unittest.main()
