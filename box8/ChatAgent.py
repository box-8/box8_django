import json
import os
import tempfile
import PyPDF2
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import (PDFSearchTool,
                          DOCXSearchTool,
                          TXTSearchTool,
                          CSVSearchTool,
                          WebsiteSearchTool,
                          ScrapeWebsiteTool)
from docx import Document
from lorem_text import lorem



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
        
    elif name=="claude":
        selected_llm = LLM(
            model="claude-3-5-sonnet-20240620",
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

    if src.startswith('http'):
        print("[INFO] Outil sélectionné : ScrapeWebsiteTool")
        return ScrapeWebsiteTool(website_url=src)
    elif src.endswith('.chat'):
        print("[INFO] Outil sélectionné : Pas de fichier")
        return None
    
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
        extension = os.path.splitext(pdf)[1].lower()

        # Extraction pour les fichiers PDF
        if extension == '.pdf':
            with open(pdf, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)

                for page_num, page in enumerate(reader.pages):
                    try:
                        texte = page.extract_text()
                        if texte:
                            texte_pages.append(texte)
                        else:
                            print(f"Le texte de la page {page_num + 1} est vide ou illisible.")
                    except Exception as e:
                        print(f"Erreur lors de l'extraction du texte de la page {page_num + 1}: {e}")

        # Extraction pour les fichiers DOCX
        elif extension == '.docx':
            try:
                doc = Document(pdf)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

                # Grouper les paragraphes par blocs de 11
                bloc = []
                for i, paragraphe in enumerate(paragraphs, start=1):
                    bloc.append(paragraphe)
                    if i % 11 == 0:
                        texte_pages.append("\n".join(bloc))
                        bloc = []

                # Ajouter les paragraphes restants si le dernier bloc a moins de 11 paragraphes
                if bloc:
                    texte_pages.append("\n".join(bloc))

            except Exception as e:
                print(f"Erreur lors de l'extraction du texte du fichier DOCX : {e}")

        else:
            print("Format de fichier non pris en charge. Seuls les fichiers PDF et DOCX sont acceptés.")

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
            expected_output=f"Un condensé en français de la page {(i +1)} dans un style concis, structuré avec des listes à puces et des titres au format markdown pour la mise en forme.",
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











""" métier CCTP """
def chat_sommaire(pdf, question , history=None, llm="openai"):    
    
    try : 
    
        lecteur = Agent(
                role="Analyste",
                goal="L'analyste extrait le informations du document de manière à remplir un tableau structuré",
                allow_delegation=False,
                verbose=True,
                backstory=f"""
                    Fort de son expertise dans le domaine de la question l'analyste extrait les informations demandées à partir du document
                    """,
                llm = ChooseLLM()
            )

        if pdf.endswith("just.chat"):
            lecteur.goal = f"""
                L'analyste répond à la question de manière à remplir un tableau structuré
            """
            lecteur.backstory=f"""
                Fort de son expertise l'analyste extrait les informations demandées permettant de structurer la réponses à la question
                    """
        else : 
            lecteur.backstory=f"""
                    Fort de son expertise en analyse de texte l'analyste littéraire extrait les informations demandées à partir du document
                    """
            lecteur.tools=[choose_tool(src=pdf)]
        
        analyseJson = Task(
            description=f"""
            Extraire les informations permettant de répondre à la question posée : 
            Question : {question}""",
            expected_output=f"""
            Un tableau json correspondant à la liste des réponses trouvées par l'analyste à la question posée.
            La structure du json à respecter : 
            [
                {{
                    "title": "nom de l'information trouvée",
                    "description": "description détaillée de la réponse "
                }},
                ...
            ]
            Retournez uniquement le JSON au format demandé sans autre explication.
            """,
            agent=lecteur,
        )
        
        crew = Crew(
            agents=[lecteur],
            tasks=[analyseJson],
            process=Process.sequential
        )

    
        result = crew.kickoff()
        donnees_json = json.loads(result.raw)
    except Exception as e:
        result = {e}
        
    return donnees_json



""" métier CCTP """
def chat_cctp_lots(pdf, question , history=None, llm="openai"):    
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
            tools=[choose_tool(src=pdf)],
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





import os
import json

def save_history(pdf, history=None, question="", response=""):
    if history is None:
        history = []

    # Le nom du fichier JSON basé sur le nom de `pdf`
    nom_fichier_json = f"{pdf}.json"

    # Lit le contenu existant du fichier s'il existe
    conversation = []
    if os.path.exists(nom_fichier_json):
        with open(nom_fichier_json, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                conversation = data.get("conversation", [])
            except json.JSONDecodeError:
                conversation = []

    # Dictionnaire pour vérifier si la question existe déjà
    found = False
    for item in conversation:
        if item["title"] == question:
            # Met à jour la réponse si la question existe déjà
            item["description"] = response
            found = True
            break

    # Si la question n'existe pas, on l'ajoute à la liste
    if not found and question:
        conversation.insert(0, {"title": question, "description": response})

    # Insère la nouvelle entrée dans l'historique si elle est fournie
    if question and response:
        history.insert(0, [question, response])

    # Utilise un dictionnaire pour éliminer les doublons (en conservant la dernière occurrence)
    seen = {}
    for item in conversation:
        seen[item["title"]] = item

    # Reconstruit la liste des conversations sans doublons
    conversation = list(seen.values())

    # Structure JSON finale
    conversation_json = {
        "conversationPath": nom_fichier_json,
        "conversation": conversation
    }

    # Enregistre l'objet JSON mis à jour dans le fichier
    with open(nom_fichier_json, "w", encoding="utf-8") as f:
        json.dump(conversation_json, f, indent=4, ensure_ascii=False)

    print(f"Conversation sauvegardée en JSON : {nom_fichier_json}")

    return conversation_json



    
    
    
def chat(pdf, question , history=None, llm="openai"):
    
    if llm =="debug":
        response = '\n\n'.join([lorem.paragraph() for _ in range(2)])

    elif pdf.endswith("just.chat"):
        response = chat_llm(question=question , history=history, llm=llm)
    else:
        response = chat_doc(pdf=pdf, question=question , history=history, llm=llm)    
    
    conversation_json = save_history(pdf=pdf, history=history, question=question, response=response)
    return response, conversation_json



def chat_doc(pdf, question , history=None, llm="openai"):
    if question=="map_plot_pdf":
        return map_plot_doc(pdf, question , history=None, llm="openai")
    if question=="map_plot_txt":
        return map_plot_doc(pdf+".txt", question , history=None, llm="openai")
    
    if history is None:
        history = []

    conversation_context = "\n".join(
        f"\nQuestion : {q}\nRéponse : {r}" for q, r in history[:5]
    )


    goal=f"""
        L'analyste répond au mieux possible à la question en lisant le document et en tenant compte du contexte de la conversation.
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
        description=f"""
        Répondre à la question posée sur le document en utilisant le contexte de la conversation.
        Question :
        {question}
        
        Contexte de la conversation :
        {conversation_context}
        """,
        expected_output=f"""
        Une réponse précise et structuré avec un titre, des sous titres et des listes à puces si nécessaire au format markdown pour la mise en forme. 
        Prendre en compte le contexte précédent et répondre dans la langue de la question.
        
        """,
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

    return result.raw


def chat_llm(question , history=None, llm="openai"):
    if history is None:
        history = []

    conversation_context = "\n".join(
        f"\nQ: {q}\nR: {r}" for q, r in history[:5]
    )

    goal=f"""
        L'analyste répond au mieux possible à la nouvelle question en tenant compte du contexte de la conversation
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
            Lecteur chevronné, l'analyste fait appel à ses connaissances pour répondre le plus précisémment possible à la question posée.
            """
        ),
        llm = ChooseLLM(llm)
    )
    repondre = Task(
        description="Répondre à la question posée sur le document en utilisant le contexte.",
        expected_output="Une réponse précise, dans la langue de la question, structuré avec des listes à puces et des titres au format markdown pour la mise en forme et prenant en compte le contexte de la conversation.",
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

    return result.raw






def chat_enhance(originalQuestion, originalText, pdf, question , history=None, llm="openai"): 
    if history is None:
        history = []
        
        
    if llm =="debug":
        response = '\n\n'.join([lorem.paragraph() for _ in range(2)])
    else:
        conversation_context = "\n".join(
            f"\nTitre du chapitre: {q}\nContenu du Chapitre: {r}" for q, r in history[:5]
        )
        goal=f"""
            L'analyste complète le texte initial en répondant à la question posée dans le contexte de la conversation.
            """

        analyste = Agent(
            role="Analyste documentaire",
            goal=goal,
            backstory=f"""
            Lecteur chevronné, l'analyste approfondit la rédaction du texte initial en développer sont contenu.
            """,
            allow_delegation=False,
            verbose=True,
            llm = ChooseLLM(llm)
        )
        if pdf.endswith("just.chat"):
            pass
        else : 
            backstory="""
                Lecteur chevronné, l'analyste recherche et extrait les données pertinentes du document ou de ses propres connaissances
                pour améliorer la rédaction du texte initial et en développer le contenu.
                """
            analyste.tools=[choose_tool(src=pdf)]
            
        description=f"""
            Reprendre l'intégralité du texte initial en y ajoutant les paragraphes nécessaires pour 
            l'approfondir par une réponse à la question posée. 
            La mise en forme initiale, les titres, les chaptitres et les listes du texte initial au format markdowd doivent être conservées 
            Question : 
            {question}
            Texte initial à complèter sans en modifier le sens ni la forme : 
            {originalText}
            Le contenu des autres chapitres peut être pris en compte pour améliorer le texte initial sans être réutilisé dans la réponse :
            {conversation_context}
            """
        
        repondre = Task(
            description=description,
            expected_output="""
            Le texte initial amélioré, structuré avec des listes à puces et des titres au format markdown pour la mise en forme. formuler les paragraphes supplémentaires dans la langue de la question
            """,
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
        response = result.raw

    conversation_json = save_history(pdf=pdf, history=history, question=originalQuestion, response=response) 
    
    return response, conversation_json
















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
    
    return fusionner_infos_geographiques(history)
    return chat_doc(pdf, question , history, llm)

    
    
    
    








def webscrap(pdf, question , history=None, llm="openai"): 
    goal=f"""
        L'analyste répond à la question posée :
        Question :
        {question}
        """

    analyste = Agent(
        role="Analyste documentaire",
        goal=goal,
        allow_delegation=False,
        verbose=True,
        backstory=(
            """
            Lecteur chevronné, l'analyste recherche et extrait les données pertinentes du document ou de ses propres connaissances.
            """
        ),
        tools=[choose_tool(src=pdf)],
        llm = ChooseLLM(llm)
    )
    
    description=f"""Etablir un résumé de la page internet et en extraire les informations clefs"""
    
    repondre = Task(
        description=description,
        expected_output="""
        Un résumé structuré, structuré avec des listes à puces et des titres au format markdown pour la mise en forme : 
        - Résumé
        - liste de points clefs
        """,
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
if __name__ == "__main__":

    print(webscrap(
        pdf="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038812251",
        question="résumer la page internet",
        llm="groq-llama"
        ))