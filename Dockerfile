FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy FASTEMBED_CACHE_PATH=/app/.models
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project
COPY src src
COPY data/docs data/docs
RUN uv sync --frozen
# bake the embedding model into the image so the app starts with no internet
RUN uv run --no-sync python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"
EXPOSE 8000
CMD ["uv", "run", "--no-sync", "shopfloor-copilot"]
