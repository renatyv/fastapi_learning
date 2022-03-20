FROM python:3.9

WORKDIR /code

# install python requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# copy code
COPY ./blog /code/blog

# start web api using uvicorn
CMD ["uvicorn", "blog.main:app", "--host", "0.0.0.0" , "--port", "8100"]

EXPOSE 8100