import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pickle
import zipfile
import shap

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
    Explorez les données de modélisation et découvrez les prédictions de score de crédit.  
    Ce tableau de bord est conçu pour répondre aux besoins des utilisateurs, y compris ceux en situation de handicap, conformément aux critères WCAG.  
    """
)

# Chargement des données
@st.cache
def load_data():
    with zipfile.ZipFile("cleaned_data.zip", "r") as z:
        with z.open("cleaned_data.csv") as f:
            return pd.read_csv(f)

@st.cache
def load_model():
    with open("model.pkl", "rb") as model_file:
        return pickle.load(model_file)

@st.cache
def load_model_columns():
    with open("model_columns.pkl", "rb") as columns_file:
        return pickle.load(columns_file)

# Charger les données et les colonnes
try:
    data = load_data()
    model = load_model()
    model_columns = load_model_columns()
    st.sidebar.success("Données, modèle et colonnes chargés avec succès !")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement des ressources : {e}")

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

# Affichage des données du client
st.sidebar.subheader("Données Client")
client_data = data[data["SK_ID_CURR"] == client_id]
st.sidebar.dataframe(client_data)

# Visualisation du score
st.sidebar.subheader("Score de Crédit")
try:
    score = model.predict_proba(client_data[model_columns])[0, 1]  # Probabilité de la classe positive
    seuil = 0.5
    st.sidebar.metric("Score de Crédit", f"{score:.2f}")
    if score >= seuil:
        st.sidebar.success("Crédit Accordé")
    else:
        st.sidebar.error("Crédit Refusé")
except Exception as e:
    st.sidebar.error(f"Erreur lors de l'évaluation du score : {e}")

# Interprétation du score
st.header("Interprétation du Score")
try:
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(client_data[model_columns])
    st_shap = lambda plot: st.components.v1.html(shap.plots.force(plot, matplotlib=True)._repr_html_(), height=300)
    st_shap(shap.force_plot(explainer.expected_value[1], shap_values[1], client_data[model_columns]))
except Exception as e:
    st.error(f"Erreur lors de l'interprétation du score : {e}")

# Visualisation des informations descriptives
st.header("Informations Clés du Client")
metrics = {
    "Revenu Annuel": client_data["AMT_INCOME_TOTAL"].values[0],
    "Montant Crédit": client_data["AMT_CREDIT"].values[0],
    "Type Contrat": client_data["NAME_CONTRACT_TYPE"].values[0]
}
for key, value in metrics.items():
    st.metric(key, value)

# Comparaison avec d'autres clients
st.header("Comparaison avec d'autres clients")
st.subheader("Filtrer par groupe")
genre = st.selectbox("Genre :", data["CODE_GENDER"].unique())
contrat = st.selectbox("Type de Contrat :", data["NAME_CONTRACT_TYPE"].unique())
filtered_data = data[(data["CODE_GENDER"] == genre) & (data["NAME_CONTRACT_TYPE"] == contrat)]
st.dataframe(filtered_data)

# Graphiques
st.header("Analyse des Revenus")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data["AMT_INCOME_TOTAL"], kde=True, bins=30, ax=ax, color="blue")
ax.axvline(client_data["AMT_INCOME_TOTAL"].values[0], color="red", linestyle="--", label="Client")
ax.set_title("Répartition des revenus")
ax.set_xlabel("Revenus")
ax.set_ylabel("Nombre de clients")
ax.legend()
st.pyplot(fig)

st.header("Montant des Crédits")
fig2 = px.box(
    data, x="NAME_CONTRACT_TYPE", y="AMT_CREDIT", color="NAME_CONTRACT_TYPE",
    title="Montants des crédits par type de contrat"
)
st.plotly_chart(fig2)

st.header("Relation Revenu-Crédit")
fig3 = px.scatter(
    data, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", color="CODE_GENDER",
    title="Revenu vs Crédit"
)
st.plotly_chart(fig3)

st.header("Répartition des Statuts Familiaux")
fig4 = px.pie(
    data, names="NAME_FAMILY_STATUS", title="Répartition des statuts familiaux"
)
st.plotly_chart(fig4)

st.markdown("**Merci d'utiliser le Dashboard Crédit Scoring !**")

