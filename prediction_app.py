# Importation des librairies
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from io import StringIO
import uvicorn
import pandas as pd
import mlflow
from pydantic import BaseModel
from typing import Union

from model import *

# Création de l'application FastAPI
app = FastAPI()

class requestObject(BaseModel):
    client_id: Union[float, None] = None
    feat_number : Union[int, None] = None
    feat_name : Union[str, None] = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Définition du endpoint de prédiction pour la décision d'octroi de crédit
# Retourne un JSON contenant la prédiction et la probabilité.
@app.post('/predict_credit_decision')
async def predict_credit_decision(data: requestObject):
    proba, prediction = predict(data.client_id)
    return {"result" : prediction, "proba" : proba}

# Définition du endpoint de retour de la liste des ID clients
# Retourne la liste des ID clients
@app.post('/get_clients_list')
async def get_clients_list():
    return {"clients_list" : clients_id_list()}

# Définition du endpoint pour récupérer les informations sur un client
@app.post('/get_client_data')
async def get_client_data(data: requestObject):
    return {"client_data" : client_info(data.client_id)}

# Définition du endpoint pour recupérer les informations générales sur le crédit demandé
@app.post('/get_credit_info')
async def get_credit_info(data: requestObject):
    return {"credit_info" : credit_info(data.client_id)}

# Définition du endpoint pour récupérer le graph SHAP waterfall
@app.post('/get_shap_waterfall_chart')
async def get_shap_waterfall_chart(data: requestObject):
    image = shap_waterfall_chart(data.client_id, data.feat_number)
    return {"base64_image" : image}

# Définition du endpoint pour récupérer le graph SHAP waterfall
@app.post('/get_shap_waterfall_chart_global')
async def get_shap_waterfall_chart_global(data: requestObject):
    image = shap_waterfall_chart_global(data.feat_number)
    return {"base64_image" : image}

# Définition du endpoint de retour de la défintion des features
@app.post('/get_features_definition')
async def get_features_definition():
    return {"feature_definition" : features_def()}

# Définition du endpoint pour récupérer le graph de comparaison du client aux autres clients
@app.post('/get_comparison_graph')
async def get_comparison_graph(data: requestObject):
    image = comparison_graph(data.client_id, data.feat_name)
    return {"base64_image" : image}