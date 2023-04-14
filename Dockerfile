FROM ghcr.io/multi-py/python-uvicorn:py3.11-0.20.0

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app app