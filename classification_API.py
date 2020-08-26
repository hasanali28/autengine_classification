from fastapi import FastAPI, File, UploadFile
from fastai.vision import *

app = FastAPI()

##loading the weights of the network
learn = load_learner("Images/models")

@app.post("/classify/")
async def read_img(file: UploadFile = File(...)):
    img = open_image(file.file)

    category = learn.predict(img)

    return {"filename": str(category[0])}