#!/bin/bash

mkdir $FILE_DIRECTORY
$(poetry env info --path)/bin/python -m uvicorn vast_file_api.main:app --host 0.0.0.0 --port 80
