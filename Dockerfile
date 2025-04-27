FROM python:3.11


RUN pip install poetry==1.7.1
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-dev
COPY . /app
CMD ["python", "main.py"]
