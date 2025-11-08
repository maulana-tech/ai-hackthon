FROM python:3.11-slim

WORKDIR /app

# Install UV package manager
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY requirements.txt ./
COPY app ./app
COPY data ./data
COPY .env.example ./.env

# Install dependencies with UV
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .

# Expose port
EXPOSE 8000

# Run the application
CMD [".venv/bin/python", "app/main.py"]
