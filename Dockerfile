# Dockerfile for FastAPI App with Multi-Worker Gunicorn + Uvicorn

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 8000

CMD ["gunicorn", "app.backend_main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000"]



# FROM python:3.10-slim

# WORKDIR /app
# COPY app /app
# COPY requirements.txt /app/

# RUN pip install --upgrade pip \
#  && pip install --no-cache-dir -r requirements.txt

# EXPOSE 8000

# CMD ["gunicorn", "fastapi_stock_advisor:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000"]
