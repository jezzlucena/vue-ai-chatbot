FROM python:3.12.8-bookworm

WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin:/home/${USERNAME}/.local/bin"
ENV PYTHONPATH=.

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt