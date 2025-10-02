FROM python:3.13-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Clean and update apt
RUN apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get update && apt-get install -y curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY src/requirements.txt .
RUN uv pip install -r requirements.txt --system

COPY src/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]