from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor import motor_asyncio
from config import BaseConfig
from routers.milsymbol_units import router as milsymbol_units_router
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("---------- TEST ----------")
    # Starting up
    app.client = motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    app.db = app.client[settings.DB_NAME]

    try:
        app.client.admin.command("ping")
        print("Pinged your deployment. You have successfully connected to MongoDB!")
        # print(f"Mongo address: {settings.DB_URL}")
    except Exception as e:
        print(e)

    yield
    # Shutting down
    app.client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(milsymbol_units_router, prefix="/units", tags=["units"])


@app.get("/")
async def get_root():
    return {"Message": "Root working"}
