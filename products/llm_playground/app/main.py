import json
import os
import warnings

warnings.filterwarnings("ignore", category=Warning)
from fastapi import FastAPI

import app

app = FastAPI(
    docs_url="/docs",
    title="JSL LLM APIs",
    swagger_ui_parameters={"tryItOutEnabled": True},
)
PORT = os.getenv("CONTAINER_PORT", 5001)
BASE_URL = f"http://localhost:{PORT}"


@app.get("/", tags=["API Documentation"], include_in_schema=False)
@app.get("/help", tags=["API Documentation"], include_in_schema=False)
async def rest_api_info():
    with open("api_info.json", "r") as f:
        json_str = f.read().replace("__PORT__", f"{PORT}")
        return json.loads(json_str)


from app.src import api

app.include_router(api.route)
