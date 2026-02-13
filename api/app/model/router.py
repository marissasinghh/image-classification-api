import os
from typing import List

from app import db
from app import settings as config
from app import utils
from app.auth.jwt import get_current_user
from app.model.schema import PredictRequest, PredictResponse
from app.model.services import model_predict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/predict")
async def predict(file: UploadFile, current_user=Depends(get_current_user)):
    rpse = {"success": False, "prediction": None, "score": None, "image_file_name": None}

    # Check if file was sent
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check if file is allowed
    if not utils.allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type is not supported.")

    # Get file name and save to disk
    image_name = await utils.get_file_hash(file)
    file_path = os.path.join(config.UPLOAD_FOLDER, image_name)

    # Save file to disk
    if not os.path.exists(file_path):
        with open(file_path, "wb") as fp:
            fp.write(await file.read())

    # Send file to model service
    prediction, score = await model_predict(image_name)

    rpse["success"] = True
    rpse["prediction"] = prediction 
    rpse["score"] = score
    rpse["image_file_name"] = image_name

    return PredictResponse(**rpse)
