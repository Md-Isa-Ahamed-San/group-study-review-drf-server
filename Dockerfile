FROM python:3.13-slim-bullseye

# Set environment variables to prevent Python from writing .pyc files to disc
# and to keep Python output unbuffered.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Clean, update apt, and install curl.
# -o Acquire::Check-Valid-Until=false bypasses errors from expired repository metadata.
# --no-install-recommends reduces the image size by only installing essential packages.
RUN apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get update -o Acquire::Check-Valid-Until=false \
 && apt-get install -y --no-install-recommends curl

# Copy the uv binary from the official astral-sh image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the requirements file and install dependencies
COPY src/requirements.txt .
RUN uv pip install -r requirements.txt --system

# Copy the rest of the application source code
COPY src/ .

# Copy and make the entrypoint script executable
COPY src/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run when the container starts
CMD ["/app/entrypoint.sh"]