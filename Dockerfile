FROM centos:9-stream-poetry AS builder

COPY poetry.lock pyproject.toml /src/
WORKDIR /src

RUN poetry install --no-dev


FROM centos:9-stream

WORKDIR /src
COPY ./ /src
COPY --from=builder /src/.venv/ /src/.venv/

EXPOSE 18000

ENTRYPOINT [ "/src/.venv/bin/gunicorn" ]
CMD [ "-c", "server.gunicorn.conf.py" ]
