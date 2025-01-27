import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Crédit Scoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre et description
st.title("Dashboard Crédit Scoring")
st.markdown(
    """
    **Bienvenue sur le tableau de bord Crédit Scoring !**  
    Explorez les données de modélisation et découvrez les décisions d'accord ou de refus de crédit.  
    Ce tableau de bord est conçu pour répondre aux besoins des utilisateurs, y compris ceux en situation de handicap, conformément aux critères WCAG.  
    """
)

# Chargement des données
@st.cache
def load_data():
    with zipfile.ZipFile("cleaned_data.zip", "r") as z:
        with z.open("cleaned_data.csv") as f:
            return pd.read_csv(f)

# Charger les données
try:
    data = load_data()
    st.sidebar.success("Données chargées avec succès !")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement des données : {e}")

# Définir les règles pour accorder ou refuser un crédit
RULES = {
    "ACCORD": [
        {"feature": "AMT_INCOME_TOTAL", "operator": ">=", "value": 50000},
        {"feature": "AMT_CREDIT", "operator": "<=", "value": 500000},
    ],
    "REFUS": [
        {"feature": "AMT_INCOME_TOTAL", "operator": "<", "value": 20000},
        {"feature": "AMT_CREDIT", "operator": ">", "value": 1000000},
    ]
}

# Vérifier si un client satisfait les règles
def check_decision(client_row):
    for rule in RULES["ACCORD"]:
        if not eval(f"{client_row[rule['feature']]} {rule['operator']} {rule['value']}"):
            return "Refusé"
    for rule in RULES["REFUS"]:
        if eval(f"{client_row[rule['feature']]} {rule['operator']} {rule['value']}"):
            return "Refusé"
    return "Accordé"

# Interface utilisateur : Sélection d'un client
st.sidebar.header("Options Utilisateur")
client_id = st.sidebar.selectbox("Sélectionnez un ID Client :", data["SK_ID_CURR"].unique())

# **1. Visualiser le score et l’interprétation**
st.header("Visualisation du Score et de l'Interprétation")
st.sidebar.subheader("Données Client")
client_data = data[data["SK_ID_CURR"] == client_id]
st.sidebar.dataframe(client_data)

# Décision basée sur les règles
st.sidebar.subheader("Décision du Crédit")
try:
    decision = check_decision(client_data.iloc[0])
    st.sidebar.write(f"**Résultat : {decision}**")
    st.write(f"### Résultat pour le client sélectionné : {decision}")
except Exception as e:
    st.sidebar.error(f"Erreur lors de l'évaluation des règles : {e}")

# **2. Visualiser les principales informations descriptives du client**
st.header("Informations Clés du Client")
metrics = {
    "Revenu Annuel": client_data["AMT_INCOME_TOTAL"].values[0],
    "Montant Crédit": client_data["AMT_CREDIT"].values[0],
    "Type Contrat": client_data["NAME_CONTRACT_TYPE"].values[0]
}
for key, value in metrics.items():
    st.metric(key, value)

# **3. Comparaison avec un groupe similaire**
st.header("Comparaison avec un Groupe")
st.subheader("Comparer avec des clients similaires")
genre = st.selectbox("Genre :", data["CODE_GENDER"].unique())
contrat = st.selectbox("Type de Contrat :", data["NAME_CONTRACT_TYPE"].unique())
filtered_data = data[(data["CODE_GENDER"] == genre) & (data["NAME_CONTRACT_TYPE"] == contrat)]

st.subheader("Visualisation des Revenus et Crédits")
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    x="AMT_INCOME_TOTAL", y="AMT_CREDIT", data=filtered_data, label="Groupe", ax=ax, color="blue", alpha=0.6
)
ax.scatter(
    client_data["AMT_INCOME_TOTAL"], client_data["AMT_CREDIT"],
    color="red", label="Client Sélectionné", s=100
)
ax.set_title("Revenu vs Montant du Crédit")
ax.set_xlabel("Revenu Annuel")
ax.set_ylabel("Montant du Crédit")
ax.legend()
st.pyplot(fig)

st.markdown("**Merci d'utiliser le Dashboard Crédit Scoring !**")

