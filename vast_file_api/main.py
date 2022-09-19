import os
import secrets
from typing import Any

import aiofiles
from fastapi import Depends, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from vast_file_api import app
from vast_file_api.data_access import FileAccess

security = HTTPBasic()


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> Any:
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"login"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"password"
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


# TODO: implement cacheing
@app.get("/text_file")  # type: ignore
async def retrieve_file(
    path: str, name: str, credentials: HTTPBasicCredentials = Depends(auth_user)
) -> dict[str, str]:
    file_access = FileAccess(aiofiles.open)
    try:
        contents = await file_access.retrieve(path, name)
        return {"name": name, "path": path, "file_contents": contents}
    except FileNotFoundError as err:
        raise HTTPException(status_code=404, detail=err.filename) from err


@app.post("/text_file")  # type: ignore
async def create_file(
    file_: UploadFile,
    name: str = Form(...),
    path: str = Form(),
    credentials: HTTPBasicCredentials = Depends(auth_user),
) -> dict[str, str]:
    file_access = FileAccess(aiofiles.open)
    try:
        await file_access.create(name, path, file_)
    except FileExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return {"name": name, "path": path}


@app.put("/text_file")  # type: ignore
async def substitute_file(
    file_: UploadFile,
    name: str = Form(...),
    path: str = Form(...),
    credentials: HTTPBasicCredentials = Depends(auth_user),
) -> dict[str, str]:
    file_access = FileAccess(aiofiles.open)
    try:
        await file_access.substitute(name, path, file_)
    except FileNotFoundError as err:
        raise HTTPException(status_code=404, detail=err.filename) from err
    return {"name": name, "path": path}


@app.patch("/text_file")  # type: ignore
async def change_file(
    file_: UploadFile,
    name: str = Form(...),
    path: str = Form(...),
    offset: int = Form(...),
    credentials: HTTPBasicCredentials = Depends(auth_user),
) -> dict[str, str]:
    file_access = FileAccess(aiofiles.open)
    try:
        await file_access.update(name, path, offset, file_)
    except FileNotFoundError as err:
        raise HTTPException(status_code=404, detail=err.filename) from err
    return {"name": name, "path": path}


@app.delete("/text_file")  # type: ignore
async def delete_file(
    name: str, path: str, credentials: HTTPBasicCredentials = Depends(auth_user)
) -> dict[str, str]:
    file_access = FileAccess(aiofiles.open)
    try:
        file_access.delete(name, path)
    except FileNotFoundError:
        pass
    return {"name": name, "path": path}


@app.get("/directory")  # type: ignore
async def list_directory(
    path: str, credentials: HTTPBasicCredentials = Depends(auth_user)
) -> list[str]:
    return os.listdir(path)
