import json
import os
import tempfile
import PyPDF2
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import PDFSearchTool, DOCXSearchTool, TXTSearchTool, CSVSearchTool, WebsiteSearchTool




def ChooseLLM(name=""):
    
    if name == "" : 
        name = "openai"

    if name=="local":
        # selected_llm = ChatOpenAI(model="mistral-7b-local", base_url="http://localhost:1552/v1")
        
        selected_llm = LLM(
            model="ollama/mistral",
            base_url="http://localhost:11434"
        )

    elif name=="mistral":
        # API_KEY = os.getenv("MISTRAL_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/mixtral-8x7b-32768")
        selected_llm = LLM(
            model="mistral/mistral-medium-latest",
            temperature=0.2
        )
        
    elif name=="groq":
        # API_KEY = os.getenv("GROQ_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/mixtral-8x7b-32768")
        selected_llm = LLM(
            model="groq/mixtral-8x7b-32768",
            temperature=0.2
        )
    
    elif name=="groq-llama":
        # API_KEY = os.getenv("GROQ_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/llama-3.1-70b-versatile")
        selected_llm = LLM(
            model="groq/llama-3.1-70b-versatile",
            temperature=0.2
        )
    
    elif name=="openai":
        selected_llm = LLM(
            model="gpt-4",
            temperature=0.2
        )

    else:
        selected_llm = LLM(
            model="gpt-3.5-turbo",
            temperature=0.2
        )
    return selected_llm




def choose_tool(src):
    """Choisit le bon outil en fonction de l'extension du fichier."""
    _, extension = os.path.splitext(src)
    extension = extension.lower()

    
    if extension == '.pdf':
        print("[INFO] Outil sélectionné : PDFSearchTool")
        return PDFSearchTool(pdf=src)
    elif extension == '.txt':
        print("[INFO] Outil sélectionné : TXTSearchTool")
        return TXTSearchTool(txt=src)
    elif extension == '.csv':
        print("[INFO] Outil sélectionné : CSVSearchTool")
        return CSVSearchTool(csv=src)
    elif extension == '.docx':
        print("[INFO] Outil sélectionné : DOCXSearchTool")
        return DOCXSearchTool(docx=src)
    else:
        return WebsiteSearchTool(website=src)
    






def chat_memorize(pdf, question , history=None, llm="openai"):
    """
    Extrait le texte de toutes les pages d'un fichier PDF, résume chaque page en tenant compte des précédentes,
    et enregistre le résumé dans un fichier texte.
    
    

    :param pdf: Chemin vers le fichier PDF.
    :param question: Question ou objectif global à considérer dans le résumé.
    :param history: Historique initial des résumés, par défaut None.
    :param llm: Modèle de langage à utiliser, par défaut "openai".
    :return: Résumé complet du document.
    """
    # Chemin du fichier de résumé
    txt_path = pdf + ".txt"
    
    
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
    resume = ""
    goal = f"""
        L'analyste documentaire résume un document page par page en se rappellant des pages précédentes. 
        """
        
    analyste = Agent(
        role="Analyste documentaire",
        goal=goal,
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            Lecteur chevronné, l'analyste effectue un résumé condensé de la page courante.
            """
        ),
        llm = ChooseLLM(llm)
    )
    for i, text in enumerate(texte_pages):
        if len(text) < 400:
            continue
        # Construire le contexte à partir des trois pages précédentes
        if i > 0:
            contexte = "\n\n".join(history[max(0, i-3):i])
        else:
            contexte = "Aucun contexte disponible, première page."
        
        
        analyste.backstory=f"""
            Lecteur chevronné, l'analyste effectue un résumé condensé de la page courante, dans le contexte des pages précédentes.
            Contexte précédent : 
            {contexte}
        """
        repondre = Task(
            description=f"""
            Condenser le texte de la page {(i +1)}.
            Page {(i +1)} : 
            {text}
            Eviter les tournures comme 'dans la continuité de la situation précédente' ou 'dans le contexte de la page précédente' pour une lecture fluide.
            """,
            expected_output=f"Un condensé en français de la page {(i +1)} dans un style concis, en utilisant le format markdown pour la mise en forme.",
            agent=analyste,
        )
        
        crew = Crew(
            agents=[analyste],
            tasks=[repondre],
            process=Process.sequential  # Exécution séquentielle des tâches
        )
        
        try:
            result = crew.kickoff()
            history.append(result.raw)  # Ajouter le résumé actuel à l'historique
            resume += result.raw + "\n\n"
        except Exception as e:
            print(f"Erreur lors du traitement de la page {i + 1} : {e}")
    
    # Enregistrer le résumé dans un fichier texte
    try:
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(resume)
        print(f"Résumé enregistré dans le fichier : {txt_path}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du résumé : {e}")
    return resume








def chat_enhance(pdf, question , history=None, llm="openai"): 
    goal=f"""
        L'analyste complète le texte initial en répondant à la question posée :
        Texte initial :
        {history}

        Nouvelle question :
        {question}
        """

    analyste = Agent(
        role="Analyste documentaire",
        goal=goal,
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            Lecteur chevronné, l'analyste recherche et extrait les données pertinentes du document ou de ses propres connaissances
            pour améliorer la rédaction du texte initial et en développer le contenu.
            """
        ),
        tools=[PDFSearchTool(pdf=pdf)],
        llm = ChooseLLM(llm)
    )
    
    description=f"""Reprendre l'intégralité du texte initial en y ajoutant les paragraphes nécessaires pour l'approfondir par une réponse à la question posée et en utilisant 
        les informations du document analysé.
        Texte initial : 
        {history}"""
    
    repondre = Task(
        description=description,
        expected_output="Le texte initial amélioré, utilisant le format markdown pour la mise en forme. formuler les paragraphes supplémentaires dans la langue de la question",
        agent=analyste,
    )
    
    crew = Crew(
        agents=[analyste],
        tasks=[repondre],
        process=Process.sequential  # Exécution séquentielle des tâches
    )
    try : 
        result = crew.kickoff()
    except Exception as e:
        result = e
    return result.raw





def chat_cctp(pdf, question , history=None, llm="openai"):    
    chef_projet = Agent(
            role="Chef de projet",
            goal="Le chef de projet coordonne les intervenants pour la rédaction du cahier des charges",
            allow_delegation=False,
            verbose=True,
            backstory=(
                f"""
                Fort de son expérience en gestion de projet de construction le chef de projet 
                coordonne les différents intervenants et s'assure de la rédaction d'un cahier des charges correspondant 
                aux besoins de l'installation à construire
                """
            ),
            tools=[PDFSearchTool(pdf=pdf)],
            llm = ChooseLLM()
        )

    
    allotissement = Task(
        description="déterminer les lots techniques nécessaires au projet de construction",
        expected_output=f"""
        Un tableau json correspondant à la liste des lots de travaux à mobiliser pour le projet.
        Les lots doivent être constitués de manière à consulter des entreprises.
        La structure du json à respecter : 
        [
            {{
                "title": "nom du lot technique en français",
                "description": "description en français des travaux fournitures et prestations à charge du lot technique"
            }},
            ...
        ]
        Retournez uniquement le JSON demandé sans autre explication.
        """,
        agent=chef_projet,
    )
    
    crew = Crew(
        agents=[chef_projet],
        tasks=[allotissement],
        process=Process.sequential
    )

    try : 
        result = crew.kickoff()
        donnees_json = json.loads(result.raw)
    except Exception as e:
        result = {e}
        
    return donnees_json








def chat_doc(pdf, question , history=None, llm="openai"):    
    if question=="map_plot_pdf":
        return map_plot_doc(pdf, question , history=None, llm="openai")
    if question=="map_plot_txt":
        return map_plot_doc(pdf+".txt", question , history=None, llm="openai")
    
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
        tools=[choose_tool(src=pdf)],
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
    
    if pdf.endswith(".txt"):
        with open(pdf, "r", encoding="utf-8") as fichier:
            contenu = fichier.read()
            texte_pages.append(contenu)
    else:
        
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

    
    
    
    





