from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from typing import Annotated
import uvicorn
from cv_parse_runnables.resume_parser import resume_parse_api
from dotenv import load_dotenv
load_dotenv()

from logger_setup import setup_logger
log_path = "logs/app.log"
logger = setup_logger(__name__, log_path)

app = FastAPI()
app.include_router(resume_parse_api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI with Azure AD authentication"}


async def main():
    try:
        config = uvicorn.Config(app=app,
                                host="127.0.0.1",
                                port=8000,
                                log_level="info")
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
    asyncio.run(main())
