import streamlit as st
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Charger les données
data = pd.read_csv("/content/cleaned_data.csv")
model = None

try:
    import pickle
    with open("/content/model.pkl", "rb") as file:
        model = pickle.load(file)
except Exception as e:
    st.error(f"Erreur lors du chargement du modèle : {e}")

# Configurer la page
st.set_page_config(page_title="Dashboard Crédit Scoring", layout="wide")

st.title("Dashboard Crédit Scoring")
st.write("Analyse des scores de crédit et visualisation des contributions des features.")

# Fonctionnalité : Sélection d'un client
client_id = st.sidebar.selectbox("Sélectionnez un ID Client", data["SK_ID_CURR"].unique())
client_data = data[data["SK_ID_CURR"] == client_id].drop(columns=["SK_ID_CURR", "TARGET"])

# Fonction : Visualiser le score de crédit
def show_score_gauge(score):
    fig, ax = plt.subplots(figsize=(5, 2))
    ax.barh(["Score"], [score], color="green" if score > 0.5 else "red")
    ax.set_xlim(0, 1)
    ax.set_title(f"Score Crédit : {score:.2f}")
    st.pyplot(fig)

# Fonction : Récupérer les scores via une API
def get_client_score(client_id):
    url = "https://<votre_lien_ngrok>.ngrok.io/predict"  # Remplacez avec votre lien Ngrok
    response = requests.post(url, json={"client_id": client_id})
    if response.status_code == 200:
        return response.json().get("score", 0)
    return None

# Afficher le score
if st.sidebar.button("Obtenir les prédictions"):
    score = get_client_score(client_id)
    if score is not None:
        st.header("Score de Crédit")
        show_score_gauge(score)

# Graphiques
st.sidebar.subheader("Analyse Bi-Variée")
feature_x = st.sidebar.selectbox("Feature X", data.columns)
feature_y = st.sidebar.selectbox("Feature Y", data.columns)

if st.sidebar.button("Afficher l'analyse bi-variée"):
    st.subheader(f"Analyse Bi-Variée : {feature_x} vs {feature_y}")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x=feature_x, y=feature_y, data=data, alpha=0.6)
    st.pyplot(fig)
