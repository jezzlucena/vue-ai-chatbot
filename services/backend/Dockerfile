FROM python:3.12.8-bookworm

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin:/home/${USERNAME}/.local/bin"
ENV PYTHONPATH=.

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ .