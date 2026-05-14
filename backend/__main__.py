import uvicorn
from . import app
from .config import config

uvicorn.run(app, host=str(config.fastapi.host), port=config.fastapi.port)
