# FastAPI blog API
Implements a blog backend API.

Functionality:
* users
  * read
  * add
* posts
  * read
  * add

Database access is configured through environment:

```env/webapi.env```

## Run in development mode
```$ uvicorn blog.main:app --reload```

Server is loaded at  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


## Database
*Not used yet*
* Built using docker, default port 5432
* Root password is set using environment in env/database.env file
* Login inside container:
```$ docker exec -it postgres psql -U postgres```
* Login locally:
* ```$ psql -h localhost -U postgres```

## Docker deployment
build and run database and web-api images:

```$ docker-compose up -d```

Deployed app: [http://127.0.0.1:8100/docs](http://127.0.0.1:8100/docs)

## Dependencies
* Python 3.9
* FastAPI
* Pydantic
* pytest
  
## Tests
user and post creation tests are implemented
```$ pytest```