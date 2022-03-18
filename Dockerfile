FROM python:3.9.11
WORKDIR /usr/src/blog

#install FastAPI and Pytest with all the requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "uvicorn blog.main:app --host 0.0.0.0 --port 8000 "]