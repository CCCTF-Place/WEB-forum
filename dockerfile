FROM python:3.12-slim

WORKDIR /app

# 安裝 Python 依賴
RUN pip install --no-cache-dir flask werkzeug markupsafe

# 複製應用程式檔案
COPY . .

# 確保上傳目錄存在
RUN mkdir -p static/user_avatar static/history

EXPOSE 5000

ENV FLASK_APP=forum.py

CMD ["flask", "--app", "forum.py", "run", "--host=0.0.0.0", "--port=5000"]