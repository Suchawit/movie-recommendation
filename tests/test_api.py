import unittest

from fastapi.testclient import TestClient

from recommender.main import app


class ApiIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_recommend_genres(self) -> None:
        payload = {
            "user_id": "A",
            "is_movie": True,
            "current_genres": ["Action"],
            "limit": 5,
        }
        resp = self.client.post("/recommend/genres", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertLessEqual(data["count"], 5)

    def test_recommend_country(self) -> None:
        payload = {
            "user_id": "A",
            "is_movie": True,
            "last_watch_country": "United States of America",
            "limit": 3,
        }
        resp = self.client.post("/recommend/country", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertLessEqual(data["count"], 3)

    def test_recommend_title(self) -> None:
        payload = {
            "user_id": "A",
            "is_movie": True,
            "last_watch_title": "Inception",
            "limit": 5,
        }
        resp = self.client.post("/recommend/title", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)


if __name__ == "__main__":
    unittest.main()
