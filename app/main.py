import os
import uvicorn
from api import app

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", 9527))

if __name__ == "__main__":
    uvicorn.run("api:app", host=APP_HOST, port=APP_PORT)