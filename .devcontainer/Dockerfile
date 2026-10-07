FROM node:22-bookworm
ARG CODEX_VERSION=0.157.1
COPY tex-packages.txt /tmp/book-tex-packages.txt
RUN apt-get update && xargs -r apt-get install -y --no-install-recommends < /tmp/book-tex-packages.txt \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @openai/codex@${CODEX_VERSION} \
    && kpsewhich biblatex.sty && kpsewhich cleveref.sty
WORKDIR /workspace
