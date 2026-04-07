FROM python:3.11-slim

# — Build-time arguments —
ARG TL_PACKAGES="\
  amsmath amssymb babel-english booktabs caption colortbl enumitem \  
  fancyhdr float fontspec framed geometry graphics hyperref listings \  
  longtable microtype multirow pdflscape rotating setspace subcaption \  
  tabularx tcolorbox titlesec tocloft unicode-math xcolor xkeyval \  
  collection-fontsrecommended collection-latexrecommended \  
"
ARG PANDOC_VERSION=3.2

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system & build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl wget ca-certificates libfontconfig1 fontconfig perl xz-utils tar gzip make gcc \
  && rm -rf /var/lib/apt/lists/*

# Install multi-arch Pandoc
RUN set -eux; \
    ARCH="$(dpkg --print-architecture)"; \
    case "$ARCH" in \
      amd64) P_ARCH=amd64 ;; \
      arm64) P_ARCH=arm64 ;; \
      *) echo "Unsupported arch $ARCH"; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/pandoc.tar.gz \
      "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-${P_ARCH}.tar.gz"; \
    tar -C /usr/local -xzf /tmp/pandoc.tar.gz --strip-components=1; \
    rm /tmp/pandoc.tar.gz

# Bootstrap TinyTeX & install curated LaTeX packages
RUN set -eux; \
    curl -fsSL https://yihui.org/tinytex/install-unx.sh | \
      sh -s - --no-admin --scheme=small; \
    /root/.TinyTeX/bin/*/tlmgr option repository https://mirror.ctan.org/systems/texlive/tlnet; \
    /root/.TinyTeX/bin/*/tlmgr update --self --no-auto-install; \
    for pkg in ${TL_PACKAGES}; do \
      /root/.TinyTeX/bin/*/tlmgr install "$pkg" || echo "⚠️  $pkg missing — continuing"; \
    done; \
    # Symlink TeX binaries (excluding tlmgr) into /usr/local/bin
    TEXDIR="$(ls -d /root/.TinyTeX/bin/* | head -n1)"; \
    for f in "$TEXDIR"/*; do \
      base="$(basename "$f")"; \
      [ "$base" = "tlmgr" ] && continue; \
      ln -s "$f" /usr/local/bin/"$base"; \
    done

# Python dependencies 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code & bundled assets
COPY src ./src
COPY templates ./templates
COPY filters ./filters
COPY fonts ./fonts


# — Expose & Run —
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
