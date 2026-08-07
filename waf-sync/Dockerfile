FROM public.ecr.aws/docker/library/python:3.12-slim

RUN pip install --no-cache-dir boto3

COPY sync.py /app/sync.py

WORKDIR /app

CMD ["python3", "sync.py"]
