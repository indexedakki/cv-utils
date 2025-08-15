""" FastAPI application for a chatbot """
# from datetime import timedelta, datetime
# from typing import Annotated
# import json
# import sys
# pylint: disable=W0718, W0611

import os
import logging
import yaml
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from cv_chatbot import main
from logger_setup import setup_logger
load_dotenv()

LOG_PATH  = "logs/app.log"
logger = setup_logger(__name__, LOG_PATH)
logger.info("Starting FastAPI application...")

def create_log_directory(log_directory='logs'):
    """ Create a directory for logs if it doesn't exist """
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

def setup_logging(default_path='log_conf.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """ Setup logging configuration """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt', encoding="utf-8") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logging.info("logging set successfully")
    else:
        logging.basicConfig(level=default_level)
        logging.info("logging set without yaml log file")

app = FastAPI()
app.include_router(main.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    """ Root endpoint """
    return {"message": "Welcome to the FastAPI with Azure AD authentication"}

async def start_server():
    """ Main function to run the FastAPI application """
    try:
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (CTRL+C). Exiting...")
    except Exception as e:
        logger.exception("Unexpected error: ", exc_info=e)
    finally:
        logger.info("Application shutdown complete.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_server())
    