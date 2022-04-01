from typing import Union, Optional, Any

from fastapi import FastAPI
from blog.api.v1 import api as api_v1
import blog.logger_config

app = FastAPI()

# Force uvicorn to emit logs using the same loguru configs
blog.logger_config.setup_logging()


# connect V1 API using prefix
app.include_router(api_v1.api_router, prefix='/api/v1')