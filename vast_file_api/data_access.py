import os
from pathlib import Path
from typing import Any, AsyncContextManager, Callable

from vast_file_api import settings


class FileAccess:
    def __init__(self, async_open: Callable[..., AsyncContextManager[Any]]) -> None:
        self.async_open = async_open

    async def retrieve(self, path: str, name: str) -> str:
        # TODO: implement pagination and return the file chunk by chank
        # for example 1024 bytes.
        file_path = settings.FILE_DIRECTORY / Path(path) / Path(name)
        async with self.async_open(file_path, mode="r") as file:
            contents: str = await file.read()
            return contents

    async def create(self, name: str, path: str, file_: Any) -> None:
        # TODO: check free space and raise an error if there is no free space.
        contents = file_.file.read()
        directory = settings.FILE_DIRECTORY / Path(path)
        if not directory.is_dir():
            directory.mkdir()

        file_path = directory / Path(name)
        async with self.async_open(file_path, mode="xb") as file:
            await file.write(contents)

    async def substitute(self, name: str, path: str, file_: Any) -> None:
        # TODO: check free space and raise an error if there is no free space.
        directory = settings.FILE_DIRECTORY / Path(path)
        file_path = directory / name
        contents = file_.file.read()
        async with self.async_open(file_path, mode="wb") as file:
            await file.write(contents)

    async def update(self, name: str, path: str, offset: int, file_: Any) -> None:
        # TODO: check free space and raise an error if there is no free space.
        directory = settings.FILE_DIRECTORY / Path(path)
        file_path = directory / name
        if file_path.is_file():
            # TODO: if the patch is less than the rest of the original
            # file after the offset.
            async with self.async_open(file_path, mode="rb") as file:
                contents = await file.read(offset)
                # TODO: read the rest of the original file
            async with self.async_open(file_path, mode="wb") as file:
                # TODO: write the rest of the file
                contents += file_.file.read()
                await file.write(contents)

    @staticmethod
    def delete(name: str, path: str) -> None:
        os.unlink(settings.FILE_DIRECTORY / Path(path) / Path(name))
