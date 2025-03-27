FROM python:3.10-slim

WORKDIR /service/app
ADD ./src/ /service/app/
COPY requirements.txt /service/app/

RUN apt-get update && apt-get install -y curl build-essential npm && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8081

ENV PYTHONUNBUFFERED 1

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=5 \
    CMD curl -s --fail http://localhost:8081/health || exit 1

CMD ["python3", "-u", "app.py"]