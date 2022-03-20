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

* PostgresSQL 14, Built using docker, default port 5432
* Root password is set using environment in env/database.env file (not commited): ```POSTGRES_PASSWORD=password```

### yoyo migrations

list migrations

```yoyo list```

apply migrations

```yoyo apply```

rollback migrations

```yoyo rollback```

sql migration scripts (DDL) are in ```db_migrations/```

configuration: ``yoyo.ini``,

database connection url with password in ``yoyo_db_credentials.ini``:

<code>[DEFAULT]<br/>
database = postgresql://blog_admin:jw8s0F4@localhost/blog_db
</code>

#### Database login
using **blog_admin** credentials from container

```docker exec -it fastapi_blog_database_1 psql -U blog_admin -d blog_db```

using **blog_admin** credentials remotely

``psql -h 127.0.0.1 -p 5432 -U blog_admin -d blog_db``

### Postgres DB initialization:
Login into docker user superuser **postgres** credentials:

```docker exec -it fastapi_blog_database_1 psql -U postgres```

create database **blog_db**

```create database blog_db;```<br/>

create role **blog_admin** and with for password

```CREATE ROLE blog_admin WITH LOGIN PASSWORD 'jw8s0F4' CREATEROLE;```

grant all privileges to blog_admin

```GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_admin;```

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