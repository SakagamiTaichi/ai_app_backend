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

# Node.jsがない場合はインストール
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

RUN curl -fsSL https://raw.githubusercontent.com/anthropics/claude-code/main/install.sh | sh