from fastapi import FastAPI
from pydantic import BaseSettings

from blog import threadpool_executor
from blog.api.v1 import api as api_v1


class BlogUrlsConfig(BaseSettings):
    URL_PREFIX_FOR_V1_API: str


app = FastAPI()


url_config = BlogUrlsConfig()


@app.on_event("shutdown")
def stop_threadpool_executor():
    threadpool_executor.teardown()


# connect V1 API using prefix
app.include_router(api_v1.api_router, prefix=url_config.URL_PREFIX_FOR_V1_API)