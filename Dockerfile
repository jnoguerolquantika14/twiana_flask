FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip --no-cache-dir install -r requirements.txt

RUN pip install pymongo[srv]

CMD ["python3","app.py"]
