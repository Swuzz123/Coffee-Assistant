FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/ /app/data/
COPY src/ ./src/
COPY backend/ ./backend/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "backend/run_api.py"]