FROM python:3.12

WORKDIR /app

COPY requirements.txt /app/lms_engine/requirements.txt
COPY requirements-dev.txt /app/lms_engine/requirements-dev.txt

RUN pip install --upgrade pip
RUN pip install -r lms_engine/requirements-dev.txt

EXPOSE 8000
