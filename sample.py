from fastapi import FastAPI, File, UploadFile
from fastai.vision import *

app = FastAPI()


@app.post("/classify/")
async def read_img(file: UploadFile = File(...)):
    img = file.file


    return {"filename": "OK"}