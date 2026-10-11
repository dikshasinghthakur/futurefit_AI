FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
# Scale horizontally: run more containers, or add --workers N per CPU core.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
