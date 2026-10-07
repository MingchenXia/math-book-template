FROM node:22-bookworm
ARG CODEX_VERSION=0.157.1
RUN apt-get update && apt-get install -y --no-install-recommends \
    git make python3 ca-certificates latexmk biber poppler-utils \
    texlive-latex-extra texlive-bibtex-extra texlive-fonts-recommended texlive-science \
    texlive-xetex texlive-luatex texlive-lang-chinese fonts-noto-cjk lmodern \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @openai/codex@${CODEX_VERSION} \
    && kpsewhich biblatex.sty && kpsewhich cleveref.sty
WORKDIR /workspace
