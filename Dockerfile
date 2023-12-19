FROM python:3.11
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && mv /root/.local/bin/poetry /usr/local/bin/
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-dev
COPY . /app
CMD ["python", "main.py"]
