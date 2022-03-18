# FastAPI blog API
Implements a blog backend API.

Functionality:
* users
  * get
  * add
* posts
  * read

## Run in development mode
```$ uvicorn blog.main:app --reload```

Server is loaded at  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Docker deployment
build docker image

```$ docker build -t blog_image .```

run docker image in container

```$ docker run -d --name bloc_container -p 8100:8100 blog_image```

Deployed app: [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Dependencies
* Python 3.9
* FastAPI
* Pydantic
* pytest
  
## Tests
only user creation tests are implemented
```$ pytest```