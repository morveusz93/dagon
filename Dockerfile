FROM python:3.11-slim

RUN pip install --no-cache-dir poetry==1.8.3
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction
COPY . /app
CMD ["python", "main.py"]
