import os
import secrets
from typing import Optional

import aiofiles
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()


class PartialFile(BaseModel):
    contents: str
    name: str
    path: str
    offset: int


class ExistingFile(BaseModel):
    contents: Optional[str]
    name: str
    path: str


class NewFile(BaseModel):
    contents: str
    name: str


def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"registered_user"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"secure_password"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/text_file")
async def retrieve_file(
    file_path: str, credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if os.path.isfile(file_path):
        async with aiofiles.open(file_path, mode="r") as f:
            contents = await f.read()
            return {"file_contents": contents}


@app.post("/text_file")
async def create_file(
    file_: NewFile, credentials: HTTPBasicCredentials = Depends(auth_user)
):
    async with aiofiles.open(file_.name, mode="w") as f:
        await f.write(file_.contents)
    return file_.dict()


@app.put("/text_file")
async def substitute_file(
    file_: ExistingFile, credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if os.path.isfile(file_.path):
        async with aiofiles.open(file_.path, mode="w") as f:
            await f.write(file_.contents)
        return file_.dict()


@app.patch("/text_file")
async def change_file(
    file_: PartialFile, credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if os.path.isfile(file_.path):
        async with aiofiles.open("ditto_moves.txt", mode="w") as f:
            f.seek(file_.offset)
            await f.write(file_.contents)
        async with aiofiles.open(file_.path) as f:
            contents = await f.read()
            updated = file_.dict()
            updated["contents"] = contents
            return updated


@app.patch("/text_file")
async def delete_file(
    file_: ExistingFile, credentials: HTTPBasicCredentials = Depends(auth_user)
):
    if os.path.isfile(file_.path):
        async with aiofiles.open(file_.path, mode="r") as f:
            contents = await f.read()
            deleted = file_.dict()
            deleted["contents"] = contents

        os.unlink(file_.path)
        return deleted


@app.get("/directory")
async def list_directory(credentials: HTTPBasicCredentials = Depends(auth_user)):
    return os.listdir()
