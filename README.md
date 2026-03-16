# Movie & TV Recommendation API

A FastAPI service that recommends Netflix movies or TV shows based on user behavior signals (genre, country, title, cast, director, description). It uses the provided CSV datasets directly without model training and is designed to emphasize production-quality ML infrastructure patterns.

## Dataset (First Step)
Download the dataset into `DSAssignmentDataSet` before running the API:

```bash
git clone https://github.com/pimphornm-pim/DSAssignmentDataSet DSAssignmentDataSet
```

## Highlights
- Clear separation of data, service, and API layers
- Dependency Injection with `dependency-injector`
- Pydantic request/response schemas
- Unit and integration tests
- Ready for containerization

## How It Works
- Loads two CSV datasets into memory on startup.
- Uses rule-based matching to score similar content by the selected signal.
- Applies optional popularity/rating filters.
- For title recommendations, boosts sequels and related titles (e.g., `Iron Man` -> `Iron Man 2/3`).
- Sorts results by relevance score, date added, popularity, and vote average.
- Returns a list of recommended movies or TV shows.

This approach is intentionally simple and transparent to satisfy the assignment requirement while showing an end-to-end ML system architecture.

## API Usage
All routes return a list of movies or TV shows. Use `is_movie` to choose the dataset.

### Base URL
`http://localhost:8000`

### Health
**GET** `/health`

### 1) Recommend by genres
**POST** `/recommend/genres`

```json
{
  "user_id": "A",
  "is_movie": true,
  "current_genres": ["Action", "Adventure"],
  "limit": 10,
  "min_popularity": 50,
  "min_rating": 6.5
}
```

### 2) Recommend by country
**POST** `/recommend/country`

```json
{
  "user_id": "A",
  "is_movie": true,
  "last_watch_country": "United States of America",
  "limit": 10
}
```

### 3) Recommend by title
**POST** `/recommend/title`

```json
{
  "user_id": "A",
  "is_movie": true,
  "last_watch_title": "Iron Man",
  "limit": 10
}
```

### 4) Recommend by cast
**POST** `/recommend/cast`

```json
{
  "user_id": "A",
  "is_movie": true,
  "last_watch_cast": "Leonardo DiCaprio",
  "limit": 10
}
```

### 5) Recommend by director
**POST** `/recommend/director`

```json
{
  "user_id": "A",
  "is_movie": true,
  "last_watch_director": "Christopher Nolan",
  "limit": 10
}
```

### 6) Recommend by description (uses last watched title)
**POST** `/recommend/description`

```json
{
  "user_id": "A",
  "is_movie": true,
  "last_watch_title": "Inception",
  "limit": 10
}
```

### Response
```json
{
  "user_id": "A",
  "count": 2,
  "results": [
    {
      "show_id": "27205",
      "type": "Movie",
      "title": "Inception",
      "director": "Christopher Nolan",
      "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ken Watanabe, Tom Hardy, Elliot Page",
      "country": "United Kingdom, United States of America",
      "date_added": "2010-07-15",
      "release_year": 2010,
      "rating": 8.369,
      "duration": "",
      "genres": "Action, Science Fiction, Adventure",
      "language": "en",
      "description": "Cobb, a skilled thief...",
      "popularity": 156.242,
      "vote_count": 37119,
      "vote_average": 8.369,
      "budget": 160000000,
      "revenue": 839030630,
      "score": 1.0
    }
  ]
}
```

## Quickstart
### 1) Install dependencies
```bash
uv sync
```

### 2) Run the API
```bash
make run
```

### 3) Run tests
```bash
make test
```

## Docker (Optional)
```bash
docker build -t movie-recommendation .
docker run -p 8000:8000 movie-recommendation
```

## Project Structure
```
.
├── DSAssignmentDataSet
│   ├── netflix_movies_detailed_up_to_2025.csv
│   ├── netflix_tv_shows_detailed_up_to_2025.csv
│   └── README.md
├── src
│   └── recommender
│       ├── config.py
│       ├── container.py
│       ├── main.py
│       ├── models.py
│       ├── repository.py
│       └── service.py
├── tests
│   ├── test_api.py
│   └── test_service.py
├── Makefile
├── Dockerfile
├── .gitignore
└── pyproject.toml
```

## ML Architecture (Production Design)
- **Data ingestion layer**: `ContentRepository` loads structured content data from CSVs. In production this would be a feature store or data warehouse.
- **Feature engineering**: Token overlap + metadata filters. In production, this becomes an embedding service or batch feature pipeline.
- **Recommendation service**: `RecommendationService` contains the business logic and ranking.
- **API layer**: FastAPI exposes endpoints with request/response schemas using Pydantic.
- **Dependency Injection**: `dependency-injector` wires config, repository, and service for easier testing and clean architecture.
- **Testing**: Unit tests for core logic and integration tests for API behavior.

## How to Improve in the Future
1. Add user history and build a real model (collaborative filtering or hybrid with content embeddings).
2. Use embeddings (e.g., Sentence Transformers) to improve title/description similarity.
3. Store data in a vector DB or feature store for faster and scalable retrieval.
4. Add caching and pagination for large result sets.
5. Introduce online evaluation and A/B testing for ranking strategies.
6. Add monitoring dashboards for latency, errors, and recommendation quality.

## Notes
- This implementation avoids training a model to satisfy the assignment requirement.
- Use `is_movie=false` to recommend TV shows instead of movies.
