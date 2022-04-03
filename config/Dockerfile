FROM python:3-alpine

WORKDIR /code

# postgres sql support and bcrypt cryptography for password hashing
RUN apk add --no-cache postgresql-libs libffi

# install python requirements
COPY config/requirements.txt /code/requirements.txt

# --virtual: install packages, those packages are not added to global packages. And this change can be easily reverted.
# saves about ~610Mb of images size
RUN \
 apk add --no-cache --virtual .build-deps build-base postgresql-dev python3-dev libffi-dev && \
 pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
 apk --purge del .build-deps

# copy code
COPY ../blog /code/blog

# start web api using uvicorn
CMD ["uvicorn", "blog.main:app", "--host", "0.0.0.0" , "--port", "8100"]

EXPOSE 8100