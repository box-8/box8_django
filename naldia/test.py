import json
import os
import markdown
from naldia import Memorizer, Chatter, openai, printc, bcolors




def returnVal(dico,key):
    if key in dico:return dico[key]
    else: return key

def PromptDesign(titre,chat):
    jsonfinal={
    "titre":titre,
    "description": "décrire le contexte et la mission réalisée par Naldéo" ,
    "client": "nom du client pour lequel la mission a été réalisée" ,
    "secteur": "secteur d'activité du client",
    "année": "année de fin de réalisation de la mission",
    "montant": "montant en euros de la mission ",

    "lieu" : "adresse du projet",
    "lat" : "coordonnées gps, latitude",
    "lon" : "coordonnées gps longitude"
    }

    tentatives = 0
    while tentatives < 3:
        jsongpt = chat.ask("""Vous êtes un assistant qui ne répond qu'en JSON.
        Extraire les informations de la fiche mission en répondant aux #questions# ci aprés sous la forme d'un JSON VALIDE respectant strictement les attributs suivants :
        {
        "description": #décrire le contexte et la mission réalisée par Naldéo# ,
        "client": #nom du client pour lequel la mission a été réalisée# ,
        "secteur": #secteur d'activité du client# ,
        "année": #année de fin de réalisation de la mission# ,
        "montant": #montant en euros de la mission (€)# ,
        }
        """)
        try:
            jsongpt = json.loads(jsongpt)
            jsonfinal["description"] = returnVal(jsongpt,"description") 
            jsonfinal["client"] = returnVal(jsongpt,"client") 
            jsonfinal["secteur"] = returnVal(jsongpt,"secteur") 
            jsonfinal["année"] = returnVal(jsongpt,"année")
            jsonfinal["montant"] = returnVal(jsongpt,"montant") 
            
            break
        except json.JSONDecodeError as e:
            print("Information techniques : erreur de décodage JSON :"+ str(e))
            tentatives += 1
            if tentatives == 3:
                print("Trop de tentatives de chargement JSON infructueuses.")

                
    tentatives = 0
    while tentatives < 3:
        jsongpt = chat.ask("""Vous êtes un ingénieur qui ne répond qu'en JSON.
        Rechercher l'addresse du client pour lequel s'est déroulée la mission et proposer une position GPS même approximative pour cette addresse. 
        Répondre aux #questions# exclusivement sous la forme d'un JSON VALIDE respectant les attributs suivants : 
        {
        "lieu" : #adresse du client pour lequel la mission est réalisée#
        "lat" : #latitude de l'adresse du projet en degrés décimaux# ,
        "lon" : #longitude de l'adresse du projet en degrés décimaux#
        }
        """)
        try:
            jsongpt = json.loads(jsongpt)
            jsonfinal["lieu"] = returnVal(jsongpt,"lieu")
            jsonfinal["lat"] = returnVal(jsongpt,"lat")
            jsonfinal["lon"] = returnVal(jsongpt,"lon")
            break
        except json.JSONDecodeError as e:
            print("Erreur de décodage JSON :"+ str(e))
            tentatives += 1
            if tentatives == 3:
                print("Information de géolocalisation : trop de tentatives de chargement JSON infructueuses.")

    return jsonfinal

chat = Chatter()
jreponse=[]
repertoire = """C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\v0\\auth\\chatapp\\sharepoint\\gael.jaunin\\fiches refs"""
fichiers = os.listdir(repertoire)

for nom_du_fichier in fichiers:
    chemin_complet = os.path.join(repertoire, nom_du_fichier)
    if nom_du_fichier.endswith(".json") or nom_du_fichier.endswith(".txt"):
        next
    else:

        printc(nom_du_fichier,bcolors.HEADER)
        document = Memorizer()
        document.setfile(chemin_complet)
        if not document.exist_info:
            document.memorize()

        if document.exist_info:
            chat.load(document)
            response = PromptDesign(nom_du_fichier, chat)
            jreponse.append(response)

print(jreponse)


nom_du_fichier = "_map.json"
chemin_du_fichier = os.path.join(repertoire, nom_du_fichier)
printc("ENREGISTREMENT "+nom_du_fichier,bcolors.HEADER)
# Ouvrir le fichier en mode écriture
with open(chemin_du_fichier, 'w') as fichier_json:
    # Écrire le dictionnaire dans le fichier au format JSON
    json.dump(jreponse, fichier_json)

print("Dictionnaire enregistré dans", chemin_du_fichier)