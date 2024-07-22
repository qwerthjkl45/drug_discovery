FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install SQLite
RUN apt-get update \
    && apt-get install -y sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY ./app /app

RUN pip install -r /app/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
