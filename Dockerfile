FROM python:3.9-bullseye AS builder

COPY poetry.lock pyproject.toml /src/
WORKDIR /src

RUN pip install poetry && \
                poetry config virtualenvs.in-project true && \
                poetry install --no-dev


FROM python:3.9-slim

WORKDIR /src
COPY ./ /src
COPY --from=builder /src/.venv/ /src/.venv/

EXPOSE 18000

ENTRYPOINT [ "/src/.venv/bin/gunicorn" ]
CMD [ "-c", "server.gunicorn.conf.py" ]
