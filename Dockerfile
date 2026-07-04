FROM python:3.11

WORKDIR /app

COPY requirements.txt .

# Force reinstall ffmpeg without cache
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
