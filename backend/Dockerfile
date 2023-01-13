FROM python:3.10-slim

WORKDIR /app

RUN python3 -m pip install -U pip

COPY ./requirements.txt .

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]