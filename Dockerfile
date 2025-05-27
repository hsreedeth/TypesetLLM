# ---------- base image ----------
FROM python:3.11-slim AS builder

# ---------- build arguments ----------
ARG TL_PACKAGES="fontspec microtype geometry xfp xcolor ragged2e booktabs \
                 longtable unicode-math listings xkeyval pdflscape rotating"

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ---------- system deps ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
       curl ca-certificates gdisk make gcc && \
    rm -rf /var/lib/apt/lists/*

# ---------- pandoc ----------
RUN curl -L -o /usr/local/bin/pandoc \
      https://github.com/jgm/pandoc/releases/download/3.2/pandoc-3.2-linux-amd64 \
    && chmod +x /usr/local/bin/pandoc

# ---------- tinytex (minimal) ----------
RUN curl -L https://yihui.org/tinytex/install-unx.sh | sh -s - --no-admin --scheme=small \
    && /root/.TinyTeX/bin/*/tlmgr install $TL_PACKAGES \
    && /root/.TinyTeX/bin/*/tlmgr path add

ENV PATH="/root/.TinyTeX/bin/universal-darwin:${PATH}"

# ---------- python deps ----------
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && poetry install --no-dev --no-root

# ---------- app code ----------
COPY src ./src
COPY templates ./templates
COPY filters ./filters
COPY assets ./assets
CMD ["uvicorn", "src.web:app", "--host", "0.0.0.0", "--port", "8000"]
