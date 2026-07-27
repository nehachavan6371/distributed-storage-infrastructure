FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY coordinator/ ./coordinator/
COPY api/ ./api/

EXPOSE 8000

CMD ["uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
