FROM python:3.10.7-bullseye

workdir /app

EXPOSE 80

ADD vast_file_api vast_file_api

ENV FILE_DIRECTORY="/app/test_files"

COPY poetry.lock .
COPY pyproject.toml .
COPY run_server.sh .

RUN chmod 777 run_server.sh

RUN pip install poetry
RUN poetry install

RUN mkdir test_files

CMD ["/app/run_server.sh"]
