from fastapi import FastAPI
from blog.api.v1 import api as api_v1

app = FastAPI()


# connect V1 API using prefix
app.include_router(api_v1.api_router, prefix='/api/v1')