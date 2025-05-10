FROM python:3.12-slim-bookworm

USER root

RUN apt-get update && \
    apt-get -y install --reinstall ca-certificates && \
    apt-get -y install software-properties-common git && \
    apt-get -y install software-properties-common && \
    pip install --upgrade pip

# プロジェクトのrequirements.txtをコピーしてインストール
COPY requirements.txt .
RUN pip install -r requirements.txt