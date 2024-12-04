import json
import os
import tempfile
import PyPDF2
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAI
from crewai import Agent, Crew, Process, Task
from crewai_tools import PDFSearchTool




def ChooseLLM(name=""):
    
    if name =="" : name = "openai"

    if name=="local":
        selected_llm = ChatOpenAI(
            model="mistral-7b-local",
            base_url="http://localhost:1552/v1"
        )
    elif name=="groq":
        API_KEY = os.getenv("GROQ_API_KEY")
        selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/mixtral-8x7b-32768")
        
    elif name=="groq-llama":
        API_KEY = os.getenv("GROQ_API_KEY")
        selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/llama-3.1-70b-versatile")
    
    elif name=="openai":
        API_KEY = os.getenv("OPENAI_API_KEY")
        selected_llm = ChatOpenAI(
            temperature=0.7,
            openai_api_base="https://api.openai.com/v1",  # Le point de terminaison de l'API OpenAI
            openai_api_key=API_KEY ,  # Remplace par ta clé API OpenAI
            model_name="gpt-4",  # Utilise GPT-4 par exemple, ou un autre modèle supporté
        )
    else:
        API_KEY = os.getenv("OPENAI_API_KEY")
        selected_llm = ChatOpenAI(
            temperature=0.7,
            openai_api_base="https://api.openai.com/v1",  # Le point de terminaison de l'API OpenAI
            openai_api_key=API_KEY ,  # Remplace par ta clé API OpenAI
        )

    return selected_llm


def chat_doc(pdf, question , history=None, llm="openai"):
    
    if question=="map_plot_doc":
        return map_plot_doc(pdf, question , history=None, llm="openai")
    
    
    
    if history is None:
        history = []

    conversation_context = "\n".join(
        f"\nQ: {q}\nR: {r}" for q, r in history
    )
    full_context = f"{conversation_context}\nQ: {question}"

    goal=f"""
        L'analyste répond au mieux possible à la nouvelle question en lisant le document et en tenant compte du contexte de la conversation
        Contexte de la conversation :
        {conversation_context}

        Nouvelle question :
        {question}
        """

    analyste = Agent(
        role="Analyste documentaire",
        goal=goal,
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            Lecteur chevronné, l'analyste recherche et extrait les données pertinentes du document 
            pour répondre le plus précisémment possible à la question posée.
            """
        ),
        tools=[PDFSearchTool(pdf=pdf)],
        llm = ChooseLLM(llm)
    )
    repondre = Task(
        description="Répondre à la question posée sur le document en utilisant le contexte.",
        expected_output="Une réponse précise, dans la langue de la question, utilisant le format markdown pour la mise en forme et prenant en compte le contexte précédent.",
        agent=analyste,
    )
    
    crew = Crew(
        agents=[analyste],
        tasks=[repondre],
        process=Process.sequential  # Exécution séquentielle des tâches
    )
    try : 
        result = crew.kickoff()
        history.append((question, result.raw))     # Ajouter la question et la réponse à l'historique
    except Exception as e:
        result = e

    return result.raw, history






"""MAPS FUNCTIONS"""
def fusionner_infos_geographiques(tableau):
    # Initialiser le tableau consolidé pour les informations géographiques
    infos_geographiques_fusionnees = []

    for objet in tableau:
        # Vérifier si l'objet contient des infos géographiques
        if "infos_geographiques" in objet and isinstance(objet["infos_geographiques"], list):
            infos_geographiques_fusionnees.extend(objet["infos_geographiques"])

    # Construire l'objet final
    resultat = {
        "infos_geographiques": infos_geographiques_fusionnees
    }
    return resultat



def map_plot_doc(pdf, question , history=None, llm="openai"):
    """
    Extrait le texte de toutes les pages d'un fichier PDF et le stocke dans une liste.

    :param pdf_path: Chemin vers le fichier PDF.
    :return: Une liste contenant le texte de chaque page.
    """
    texte_pages = []
    try:
        # Ouvrir le fichier PDF
        with open(pdf, 'rb') as pdf_file:
            # Créer un objet lecteur PDF
            reader = PyPDF2.PdfReader(pdf_file)

            # Boucler sur toutes les pages du PDF
            for page_num, page in enumerate(reader.pages):
                try:
                    # Extraire le texte de la page et l'ajouter à la liste
                    texte_pages.append(page.extract_text())
                except Exception as e:
                    print(f"Erreur lors de l'extraction du texte de la page {page_num + 1}: {e}")

    except FileNotFoundError:
        print(f"Le fichier {pdf} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

    # analyse json de chaque page
    history = []
    for i, text in enumerate(texte_pages):
        print(f"Page {i + 1}:\n{text}\n")
        task = """
Extraire les informations géographiques présentes dans le texte de cette page (pays, villes, adresses). 15 au maximum.
Pour chacune d'elle décrire son contexte et affecter une position GPS VALIDE en degrés décimaux, en lattitude et longitude, la plus précise possible.
Remplir la liste des informations géographiques dans un tableau respectant strictement le format JSON suivant pour chaque réponse :
{
    "infos_geographiques":[
        {
            "title" : titre de l'information géographique retenue,
            "contexte" : raison et contexte pour lesquels l'information géographique est retenue (personne, activité, entreprise, tâche),
            "page": """+str(i + 1)+""",
            "lat": latitude du lieu,
            "lng": longitude du lieu
        },
    ]
}
        """
        analyste = Agent(
        role="Analyste géographique",
        goal=f"""Votre but est de positionner sur une carte géographiques présentes dans le texte suivant : 
        {text}
        Votre réponse est un JSON valide, avec des informations en français. 
        """,
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            L'analyste permet de positionner les données d'un document sur une carte, il ne réponse qu'en Json d'apérés le format demandé.
            """
        ),
        llm = ChooseLLM(llm)
    )
        repondre = Task(
            description=task,
            expected_output="Un tableau json respectant le format demandé.",
            agent=analyste,
        )
        
        crew = Crew(
            agents=[analyste],
            tasks=[repondre],
            process=Process.sequential  # Exécution séquentielle des tâches
        )
        
        try : 
            result = crew.kickoff()
            donnees_json = json.loads(result.raw)
            history.append(donnees_json)     # Ajouter la réponse à l'historique
        except Exception as e:
            result = e
    
    return fusionner_infos_geographiques(history), history
    return chat_doc(pdf, question , history, llm)

    

def CV(file="", offre_emploi=""):
    candidat = Agent(
        role="Candidat à l'offre d'emploi",
        goal="Le candidat cherche à répondre au mieux possible à l'offre d'emploi",
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            Fort de son expérience, le candidat recherche et extrait les données pertinentes de son curriculum vitae 
            pour répondre le plus précisémment possible aux attentes du recruteur.
            """
        ),
        tools=[PDFSearchTool(pdf=file)],
        llm = ChooseLLM()
    )

    recruteur = Agent(
        role="Recruteur",
        goal="Le recruteur recherche un candidat dont le profil correspond au poste dans l'entreprise",
        allow_delegation=False,
        verbose=True,
        backstory=(
            f"""
            Le recruteur interroge le candidat de manière à contrôler l'adéquation du CV du candidat pour le poste proposé par l'entreprise.
            Il rédige un mémo des forces et faiblesses du profil pour le poste.
            """
        ),
        llm = ChooseLLM()
    )


    entretien_recrutement = Task(
        description="interroger le candidat sur la pertinence de son CV lors de l'entretien d'embauche.",
        expected_output=f"""
        Un mémo à l'attention de la direction RH de l'entreprise détaillant les forces et les faiblesses du candidat pour le poste.
        Le poste est le suivant : 
        {offre_emploi}
        
        Le mémo comporte 4 sections : 
        1- les coordonnées du candidat
        2- les forces
        3- les faiblesses 
        4- une synthèse
        """,
        agent=candidat,
    )
            
    crew = Crew(
        agents=[recruteur,candidat],
        tasks=[entretien_recrutement],
        process=Process.sequential  # Exécution séquentielle des tâches
    )
    result = crew.kickoff()
    return result.raw