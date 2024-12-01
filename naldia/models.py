import os
# from matplotlib import pyplot as plt
import plotly.express as px
import base64
from io import BytesIO
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib
from sklearn.preprocessing import OneHotEncoder


excelFile = 'C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\trainningsets\\Data-TLSE-PalaysEUEP.xlsx'

def train_model(pathtoDataset, modelName="prix_prediction"):

    excelFile = os.path.join(pathtoDataset,modelName+".xlsx")
    df = pd.read_excel(excelFile)
    # Variable indépendante (description textuelle)
    X_text = df['description_prestation']  
    # Variable dépendante
    y = df['prix']  

    # Diviser les données en ensembles d'entraînement et de test
    X_train_text, X_test_text, y_train, y_test = train_test_split(X_text, y, test_size=0.2, random_state=42)

    vectorizer = CountVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train_text)
    X_test_vec = vectorizer.transform(X_test_text)

    model = LinearRegression()
    model.fit(X_train_vec, y_train)

    X_test_vec = vectorizer.transform(X_test_text)
    predictions = model.predict(X_test_vec)
    mse = round(mean_squared_error(y_test, predictions),3)
    
    print(f'Erreur quadratique moyenne : {mse}')
    
    # Afficher les prédictions par rapport aux valeurs réelles
    # Créer un graphique Scatter avec Plotly Express
    fig = px.scatter(x=y_test, y=predictions, labels={'x': 'Prix Réel', 'y': 'Prédictions de Prix'}, title='Régression Linéaire - Prédictions vs Réalité')
    # Définir la taille en pixels du graphique
    fig.update_layout(width=1200, height=900)
    # Convertir le graphique en base64
    buffer = BytesIO()
    fig.write_image(buffer, format="png")
    buffer.seek(0)
    plot_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Sauvegarder le modèle
    joblib.dump(model, modelName+'_model.joblib')
    # Sauvegarder le vectoriseur
    joblib.dump(vectorizer, modelName+'_vectoriseur.joblib')

    response = {"accuracy" : mse, "content" : plot_base64}
    return response


class DPGF:
    def __init__(self, modelName):
        # Charger le modèle
        self.loaded_model = joblib.load(modelName+'_model.joblib')
        # Charger le vectoriseur
        self.loaded_vectorizer = joblib.load(modelName+'_vectoriseur.joblib')

    

    def ask(self, question="pose d'un enrobé bichouche"):
        nouvelle_description_vec = self.loaded_vectorizer.transform([question])
        prix_predit = self.loaded_model.predict(nouvelle_description_vec)
        print(f"""Le prix prédit pour la prestation "{question}" est : {prix_predit[0]}""")
        return round(prix_predit[0],2)
        

if False:
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    def train_model_with_unit(modelName="prix_unit_prediction"):

        # Charger les données depuis le fichier Excel
        df = pd.read_excel(excelFile)
        print(df.head())
        df.info()
        
        # Normaliser les unités de prix
        df['unit'] = df['unit'].apply(lambda x: x.lower().strip())  # Convertir en minuscules et supprimer les espaces

        # Séparer les données en ensemble d'entraînement et ensemble de test
        train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

        # Définir les caractéristiques (description prestation) et les cibles (prix et unité de prix)
        X_train = train_data['description_prestation']
        y_train_prix = train_data['prix']
        y_train_unite = train_data['unit']


        # Créer un pipeline avec un préprocesseur pour le texte et un modèle de régression linéaire
        model = Pipeline([
            ('preprocessor', ColumnTransformer(
                transformers=[
                    ('description', CountVectorizer(), 'description_prestation'),
                    ('unit', OneHotEncoder(), ['unit'])  # Utiliser OneHotEncoder pour la colonne 'unit'
                ],
                remainder='passthrough'
            )),
            ('regressor', LinearRegression())
        ])

        # Entraîner le modèle
        model.fit(X_train, {'prix': y_train_prix, 'unit': y_train_unite})

        # Utilisation du modèle pour estimer le prix et l'unité associée
        prestation_a_estimer = ["poser un tuyau fonte"]
        predictions = model.predict(prestation_a_estimer)

        prix_estime = predictions['prix'][0]
        unite_prix_estimee = predictions['unit'][0]
        print(f"Estimation du prix pour la prestation '{prestation_a_estimer[0]}': {prix_estime} {unite_prix_estimee}")
            
        # Sauvegarder le modèle
        joblib.dump(model, modelName+'.joblib')


    train_model_with_unit()

    # Utilisation du modèle sauvegardé
    loaded_model = joblib.load('prix_unit_prediction.joblib')

    # Exemple de réutilisation ultérieure
    prestation_a_estimer = ["poser un tuyau fonte"]
    predictions = loaded_model.predict(prestation_a_estimer)

    prix_estime = predictions['prix'][0]
    unite_prix_estimee = predictions['unité'][0]

    print(f"Estimation du prix pour la prestation '{prestation_a_estimer[0]}': {prix_estime} {unite_prix_estimee}")







