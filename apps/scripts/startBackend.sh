#!/bin/bash

#navigate to the backend directory
cd ../backend

#install dependencies
pip install -r requirements.txt

#start the backend server
uvicorn main:app --reload