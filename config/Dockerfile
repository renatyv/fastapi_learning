FROM python:3-alpine

WORKDIR /code

# postgres sql support and bcrypt cryptography for password hashing
RUN apk add --no-cache postgresql-libs libffi

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
# install poetry
RUN \
 apk add --no-cache --virtual .build-deps build-base python3-dev libffi-dev && \
 pip3 install poetry && \
 apk --purge del .build-deps
# Do not create venv
RUN poetry config virtualenvs.create false

# install python requirements
#COPY config/requirements.txt /code/requirements.txt
COPY pyproject.toml /code

# --virtual: install packages, those packages are not added to global packages. And this change can be easily reverted.
# saves about ~610Mb of images size
RUN \
 apk add --no-cache --virtual .build-deps build-base postgresql-dev python3-dev libffi-dev && \
 poetry install --no-dev && \
 apk --purge del .build-deps

# copy code, relative to root project dir
COPY ./blog /code/blog

# start web api using uvicorn
CMD ["poetry run uvicorn", "blog.main:app", "--host", "0.0.0.0" , "--port", "8100"]

EXPOSE 8100