FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY DSAssignmentDataSet ./DSAssignmentDataSet

RUN pip install --no-cache-dir uv \
    && uv sync --frozen

ENV PYTHONPATH=src
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "recommender.main:app", "--host", "0.0.0.0", "--port", "8000"]
