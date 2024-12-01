FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm

RUN npm install -g js-yaml iconv-lite

COPY . /app

EXPOSE 19527

# 设置环境变量 API_KEY
ENV API_KEY=""

CMD ["gunicorn", "--bind", "0.0.0.0:19527", "--timeout", "1800", "app:app"]
