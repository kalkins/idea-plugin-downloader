from python:3.10

ARG CONFIG_FILE=config.yml

WORKDIR /app

RUN mkdir output

COPY ./src/requirements.txt ./
RUN pip install -r requirements.txt

COPY ./src/main.py ./
COPY ./$CONFIG_FILE ./config.yml

CMD ["python", "main.py", "-v", "-c", "config.yml", "-o", "output"]
