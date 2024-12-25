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
    elif name=="groq-llama3":
        # API_KEY = os.getenv("GROQ_API_KEY")
        # selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="groq/llama-3.1-70b-versatile")
        selected_llm = LLM(
            model="groq/llama3-8b-8192",
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
    


def extract_pages(src):
    texte_pages = []

    try:
        extension = os.path.splitext(src)[1].lower()

        # Extraction pour les fichiers PDF
        if extension == '.pdf':
            with open(src, 'rb') as pdf_file:
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
                doc = Document(src)
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
        print(f"Le fichier {src} est introuvable.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    
    return texte_pages






def chat_summarize (pdf, pages=6 , history=None, llm="openai"):
    """
    Extrait des insights à partir d'un document PDF en utilisant CrewAI.

    Paramètres :
    - pdf (str) : Le chemin vers le fichier PDF à analyser.
    - pages (str) : nombre de pages.
    - history (list, optionnel) : Un historique des interactions précédentes (par défaut, None).
    - llm (str) : Le modèle de langage à utiliser (par défaut, "openai").

    Retourne :
    - list : Une liste d'insights sous forme de tableau JSON.
    """
    firstpages = extract_pages(src=pdf)
    # Prendre uniquement les 6 premières pages
    try:
        entier = int(pages)
    except ValueError:
        print("La chaîne ne peut pas être convertie en entier")
        entier = 6
        
    content = "\n".join(firstpages[:entier])

    # Définition des agents
    title_extractor = Agent(
        name="Title Extractor",
        role="Expert en identification de titres",
        goal="Identifier le titre du document",
        backstory=f"""
            Un spécialiste dans l'identification rapide de titres et de sujets principaux 
            à partir d'extraits de documents textuels."""
    )

    author_audience_extractor = Agent(
        name="Author and Audience Extractor",
        role="Expert en analyse d'auteur et de public cible",
        goal="Identifier qui a écrit le document et à qui il est adressé",
        backstory="""
            Un analyste expérimenté capable de déduire l'auteur et le public cible 
            d'un texte en étudiant le style et le contenu."""
    )

    subject_purpose_extractor = Agent(
        name="Subject and Purpose Extractor",
        role="Expert en analyse de contenu",
        goal="Déterminer le sujet du document et son but",
        backstory="""
            Un expert en compréhension et analyse de texte, capable de résumer 
            les thèmes principaux et les objectifs sous-jacents d'un document."""
    )

    # Définition des tâches
    title_task = Task(
        name="Extraction du titre",
        agent=title_extractor,
        description=f"""
            À partir du texte suivant, identifie le titre du document :
            {content}""",
        expected_output="Le titre du document."
    )

    author_audience_task = Task(
        name="Identification de l'auteur et du public cible",
        agent=author_audience_extractor,
        description=f"""
            En te basant sur le texte suivant, détermine qui a écrit le document 
            et à quel public il s'adresse :
            {content}""",
        expected_output="L'auteur du document et le public cible."
    )

    subject_purpose_task = Task(
        name="Analyse du sujet et du but",
        agent=subject_purpose_extractor,
        description=f"""
            Analyse le texte suivant pour déterminer le sujet du document et son objectif :
            {content}""",
        expected_output="Le sujet et le but du document avec un titre des sous titres et structuré au format markdown."
    )

    # Création de l'équipe CrewAI
    crew = Crew(
        agents=[title_extractor, author_audience_extractor, subject_purpose_extractor],
        tasks=[title_task, author_audience_task, subject_purpose_task]
    )

    # Exécution des tâches par les agents
    result = crew.kickoff()
    summary = result.raw
    print(summary)
    # Retourner le résultat final
    # Enregistrer le résumé dans un fichier texte
    # Chemin du fichier de résumé
    txt_path = pdf + ".txt"
    try:
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write(summary)
        print(f"Résumé enregistré dans le fichier : {txt_path}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du résumé : {e}")
    return summary




def chat_summarize_ifnotexists(pdf, pages=6 , history=None, llm="openai"):
    
    txt_path = pdf + ".txt"
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as file:
                content = file.read()  # Lire tout le contenu du fichier
            print(f"Contenu du fichier :\n{content}")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
    else:
        print(f"Le fichier {pdf} n'existe pas, on le génère.")
        content = chat_summarize(pdf, pages=pages , history=history, llm=llm)
    return content


def extract_insights(pdf, pages=6 , history=None, llm="openai"):
    try:
        pages = int(pages)
    except ValueError:
        print("La chaîne ne peut pas être convertie en entier")
        pages = 6
    summary = chat_summarize_ifnotexists(pdf=pdf, pages=pages , history=history, llm=llm)
    insight_extractor = Agent(
        name="Insight Extractor",
        role="Analyste de contenu",
        goal="Identifier des insights clés à partir du résumé",
        verbose=True,
        tools=[choose_tool(src=pdf)],
        backstory="""
            Un expert en extraction d'insights, capable de trouver des informations 
            précieuses et des observations pertinentes dans le texte."""
    )

    insight_task = Task(
        description=f"""
        Analyse le texte suivant et identifie les insights clés du document sachant que le résumé du document est le suivant : 
        {summary}""",
        expected_output=f"""
        Un tableau json correspondant à la liste des insights.
        La structure du json à respecter : 
        [
            {{
                "title": "nom de l'insight",
                "description": "description détaillée de l'insight et de la raison pour laquelle il a été formulé"
            }},
            ...
        ]
        Retournez uniquement le JSON au format demandé sans autre explication.
        """,
        agent=insight_extractor,
    )
    
    crew = Crew(
        agents=[insight_extractor],
        tasks=[insight_task],
        process=Process.sequential
    )
    result = crew.kickoff()
    donnees_json = json.loads(result.raw)
    
    return donnees_json





""" métier sommaire """
def chat_sommaire_old(pdf, question , history=None, llm="openai"):    
    
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






def chat_memorize_old(pdf, question , history=None, llm="openai"):
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
    
    texte_pages = extract_pages(pdf)
    
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




def chat_save_conversation(src, history=None):
    if history is None:
        history = []
    
    # Convertit l'historique au format title/description
    conversation = []
    for qa_pair in reversed(history):
        question = qa_pair[0]
        response = qa_pair[1]
        conversation.append({
            "title": question,
            "description": response
        })

    # Structure JSON finale
    conversation_json = {
        "conversationPath": src,
        "conversation": conversation
    }

    # Enregistre l'objet JSON mis à jour dans le fichier
    with open(src, "w", encoding="utf-8") as f:
        json.dump(conversation_json, f, indent=4, ensure_ascii=False)

    print(f"Conversation sauvegardée en JSON : {src}")

    return conversation_json


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


def delete_entry(pdf, title_to_delete):
    # Le nom du fichier JSON basé sur le nom de `pdf`
    nom_fichier_json = f"{pdf}.json"

    # Vérifie si le fichier existe
    if not os.path.exists(nom_fichier_json):
        print(f"Le fichier {nom_fichier_json} n'existe pas.")
        return None

    # Lit le contenu existant du fichier
    try:
        with open(nom_fichier_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            conversation = data.get("conversation", [])
    except json.JSONDecodeError:
        print(f"Erreur de lecture du fichier {nom_fichier_json}.")
        return None

    # Filtre les conversations pour exclure l'entrée avec le `title` donné
    conversation_updated = [item for item in conversation if item["title"] != title_to_delete]

    # Vérifie si une entrée a été supprimée
    if len(conversation) == len(conversation_updated):
        print(f"Aucune entrée trouvée avec le titre : {title_to_delete}")
        return None

    # Structure JSON finale mise à jour
    conversation_json = {
        "conversationPath": nom_fichier_json,
        "conversation": conversation_updated
    }

    # Écrit le contenu mis à jour dans le fichier
    with open(nom_fichier_json, "w", encoding="utf-8") as f:
        json.dump(conversation_json, f, indent=4, ensure_ascii=False)

    print(f"Entrée avec le titre '{title_to_delete}' supprimée du fichier : {nom_fichier_json}")

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
            Lecteur chevronné, l'analyste approfondit la rédaction du texte initial et en développer son contenu.
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

    
    
def reorder_agents(json_data):
    # Extraire les liens et les noeuds
    links = json_data['links']
    nodes = json_data['nodes']

    # Créer un dictionnaire pour les noeuds par clé
    node_dict = {node['key']: node for node in nodes}

    # Extraire l'ordre des clés dans les relations from/to
    # On commence par le premier "from" qui est le patient
    ordered_keys = []
    # Dictionnaire pour vérifier les relations existantes
    visited = set()

    # Ajouter toutes les clés "from" dans l'ordre des relations
    for link in links:
        from_key = link['from']
        if from_key not in visited:
            ordered_keys.append(from_key)
            visited.add(from_key)
        to_key = link['to']
        if to_key not in visited:
            ordered_keys.append(to_key)
            visited.add(to_key)

    # Ajouter la clé "output" à la fin
    if 'output' not in visited:
        ordered_keys.append('output')

    # Reorganiser les noeuds en suivant l'ordre des clés dans ordered_keys
    ordered_nodes = [node_dict[key] for key in ordered_keys]

    # Retourner le json avec les nodes réorganisés
    return {
        "nodes": ordered_nodes,
        "links": links
    }
    
def crewai_launch_process(request, folder, llm="openai"):
    try:
        print(llm)
        reorder_agents
        data = json.loads(request.body)
        data = reorder_agents(data)

        nodes = data.get('nodes', [])
        links = data.get('links', [])

        # Create CrewAI agents
        agents = {}  # Changed from list to dictionary
        
        last_node_index = len(nodes) - 1
        
        for index, node in enumerate(nodes):
            role = node.get('role', '')
            key = node.get('key', '')
            
            if key=="output":
                continue
            else:    
                # print(f"New Agent : {role}")
                file = node.get('file', '')
                src = os.path.join(folder, file) if file else ""
                agent = Agent(
                    role=role,
                    goal=node.get('goal', ''),
                    backstory=node.get('backstory', ''),
                    allow_delegation=False,
                    verbose=True,
                    # verbose=(index == last_node_index),
                    llm = ChooseLLM(llm)
                )
            
                if os.path.exists(src) and file!="":
                    agent.tools = [choose_tool(src=src)]
                    print(src)
                
                agents[node.get('key')] = agent  # Store agent with its node ID as key
        

        # Create CrewAI tasks from links
        tasks = []
        for link in links:
            from_agent = agents.get(link['from'])
            to_agent = agents.get(link['to'])
            print(f"-Tache : {link['description']}")
            print(f"  - Agent : {from_agent.role}")
            
            if from_agent :
                task = Task(
                    description=link['description'],
                    agent=from_agent,
                    expected_output=link.get('expected_output', ''),
                )
                tasks.append(task)
        
        # Create and process the crew
        crew = Crew(
            agents=list(agents.values()),  # Convert agents dict values to list
            tasks=tasks
        )
        
        # Start the process (you might want to do this asynchronously)
        kickoff = crew.kickoff()
        result = ""
        for task in tasks:
            task_output = task.output
            print(f"\n\n\n----------------------------------------------------")
            print(f"Task Description: {task_output.description}")
            print(f" - Task Agent: {task_output.agent}")
            print(f" - - - ")
            print(f"Raw Output: {task_output.raw}")
            result += f"\n\n***"
            result += f"\n\n# {task_output.description}"
            result += f"\n\n## {task_output.agent}"
            result += f"\n\n{task_output.raw}"
            


        return ({
            'status': 'success',
            'message': result,
            'agents_count': len(agents),
            'tasks_count': len(tasks)
        })
    
    
    except Exception as e:
        print("error 7" + str(e))
    
        return {
            'status': 'error',
            'message': "ERROR " + str(e)
        }

    




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