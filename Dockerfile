FROM python:3.9

WORKDIR /code

#install FastAPI and Pytest with all the requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./blog /code/blog

CMD ["uvicorn", "blog.main:app", "--host", "0.0.0.0" , "--port", "8100"]

EXPOSE 8100