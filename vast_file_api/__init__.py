from fastapi import FastAPI
from pydantic import BaseSettings

app: FastAPI = FastAPI()


class Settings(BaseSettings):  # type: ignore
    FILE_DIRECTORY: str


settings: Settings = Settings()
