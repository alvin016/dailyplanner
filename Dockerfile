# 使用官方 Python 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴（若有使用 MySQL、Pillow、psycopg2 之類會需要）
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製專案原始碼
COPY . .

# 對外開放 port
EXPOSE 8002

# 預設執行指令
CMD ["gunicorn", "schedule.wsgi:application", "--bind", "0.0.0.0:8000"]
