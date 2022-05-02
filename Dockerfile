from python:3.10

ARG CONFIG_FILE=config.yml
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID -o plugins
RUN useradd -m -u $UID -g $GID -o plugins
USER plugins

WORKDIR /app

COPY ./src/requirements.txt ./
RUN pip install -r requirements.txt

COPY ./src/main.py ./
COPY ./$CONFIG_FILE ./config.yml

CMD ["python", "main.py", "-v", "-c", "config.yml", "-o", "output"]
