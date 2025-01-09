# projet-7-openclassroom
# Implémentez un Modèle de Scoring

## Introduction & Contexte
**Problématique :** 
- L'entreprise **« Prêt à dépenser »** souhaite créer un outil de scoring crédit pour :
  - Estimer la probabilité de remboursement d'un client.
  - Classifier les demandes en crédit accordé ou refusé.

**Approche :**
- Utilisation d'un dataset issu d'un concours Kaggle (clos) pour :
  - Explorer et préparer les données.
  - Modéliser une classification binaire avec gestion du déséquilibre des classes.
  - Intégrer le modèle dans un système industriel.

**Objectif final :**
- Fournir une API fonctionnelle capable de produire des prédictions fiables pour des applications de scoring crédit.

---

## Préparation des Données
### Exploratory Data Analysis (EDA)
**Pourquoi effectuer l'EDA ?**
- Identifier les caractéristiques clés des données et évaluer leur qualité.
- Détecter les valeurs aberrantes, les corrélations et les tendances.

**Analyse des variables clés :**
- **Âge (DAYS_BIRTH)** : Principal facteur influençant le remboursement.
- **EXT_SOURCE_1 à EXT_SOURCE_3** : Variables utiles mais avec des sources inconnues, à traiter avec prudence.

**Nettoyage des données :**
- Suppression des variables inutiles pour réduire le bruit et améliorer l'efficacité.
- Gestion des valeurs manquantes (e.g., méthodes de remplacement par médiane ou moyenne).

### Feature Engineering
**Pourquoi effectuer cette étape ?**
- Enrichir le modèle avec des variables plus pertinentes pour la prédiction.

**Transformations :**
- **OneHotEncoder** pour les variables catégorielles.
- **TargetEncoder** pour capturer la corrélation entre catégories et variable cible.

**Création de nouvelles variables :**
- Ratios comme revenu/emprunt pour comparer les charges financières des individus.
- Interactions entre les variables pour capturer des relations complexes.

**Transformations mathématiques :**
- Logarithmes pour réduire les skewness dans les distributions.
- Standardisation pour uniformiser les échelles des variables.

**Vérifications essentielles :**
- **Data Leakage :** éliminer les variables corrélées à la cible mais non disponibles a priori.

---

## Modélisation et Évaluation
### Stratégie de Modélisation
**Pourquoi tester plusieurs modèles ?**
- Trouver le meilleur compromis entre performance, temps de calcul et interprétabilité.

**Approche progressive :**
- Modèles simples : Regression Logistique, DummyClassifier.
- Modèles complexes : Random Forest, XGBoost.

### Gestion du déséquilibre des classes
**Pourquoi ?**
- Éviter que le modèle ne prédise principalement la classe majoritaire.

**Méthodes appliquées :**
- Random Under-Sampling pour équilibrer sans créer de données artificielles.
- SMOTE pour générer des exemples synthétiques.

### Critères d’évaluation
**Pourquoi choisir le score metier ?**
-  il permet de traduire les prédictions techniques en décisions alignées sur les objectifs stratégiques et opérationnels du métier.
**Autres indicateurs :**
- Matrice de confusion pour analyser les erreurs critiques (FN/FP).
- Temps d'entraînement pour évaluer la faisabilité industrielle.

**Validation croisee :**
- GridSearchCV pour optimiser les hyperparamètres.
- Validation croisee stratifiée pour éviter le sur-apprentissage.

**Analyse des résultats :**
- Feature Importance : Importance moyenne avec SHAP.
- Analyse locale : Impact sur des prédictions individuelles.

---

## Pipeline et Industrialisation
### Reproductibilité
**Pourquoi un pipeline ?**
- Assurer que le processus est répétable et adaptable à de nouvelles données.

**Mise en place :**
- Préparation des données.
- Entraînement et sauvegarde des modèles (pickle).

### Intégration & Déploiement
**Déploiement local avec FastAPI :**
- Créer une API capable de recevoir des requêtes JSON et de retourner des prédictions.

**Utilisation de Ngrok :**
- **Pourquoi ?** Fournir une URL publique temporaire pour tester l'API en ligne sans serveur cloud complet.
- **Comment ?** Ngrok crée un tunnel sécurisé entre le serveur local et Internet, accessible pour les tests ou démonstrations.

**Gestion des versions :**
- Stockage du code sur GitHub avec suivi des modifications.

---

## Suivi de Performance et Maintenance
### Stratégie de Suivi
**Pourquoi surveiller les performances ?**
- Identifier les dégradations dues au data drift ou aux changements dans les données.

**Outils :**
- Evidently pour générer des tableaux HTML d’analyse automatique.
- Alertes pour notifier les déviations significatives.

### Améliorations continues
- Simulation de scénarios pour anticiper les problèmes (e.g., drifts).

---

## Conclusion & Résultats
**Pourquoi cette approche est efficace ?**
- Intégration rigoureuse des meilleures pratiques de machine learning et d’industrialisation.

**Résultats obtenus :**
- Modèle final performant avec un AUC proche de 0.82.
- API déployée et accessible via Ngrok.

**Recommandations :**
- Enrichir les données pour améliorer la robustesse des prédictions.
- Tester d’autres architectures comme les réseaux neuronaux pour des patterns plus complexes.

