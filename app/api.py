from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from model import Predictor

class Record(BaseModel):
    """
    Defines fields each record should contain
    """
    id: str
    text: str

class Request(BaseModel):
    """
    Defines fields each request should contain
    """
    fromLang: str
    records: List[Record]
    toLang: str

class Payload(BaseModel):
    """
    Defines field each payload should contain
    """
    payload: Request

model = Predictor()

app = FastAPI(
    title="M2M Machine Translation",
    description="Perform machine translation through post requests"
)

@app.get("/")
def home():
    return "Welcome to M2M translation"

@app.post("/translation")
def translation(body: Payload):
    try:
        global model
        payload = body.payload
        results = model.get_predictions(payload.records, payload.fromLang, payload.toLang)
        return {"result": results}
    except KeyError:
        raise HTTPException(status_code=409, detail=f'Invalid request format or missing required parameters.')
