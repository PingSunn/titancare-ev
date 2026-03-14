FROM python:3.13-slim

# Install Node.js (required by prisma-client-py to generate the client)
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy Prisma schema and generate client
COPY prisma/ ./prisma/
RUN uv run prisma generate

# Copy source code and brochures
COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"]
