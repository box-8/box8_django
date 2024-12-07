import json
import os
import re
from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from lorem_text import lorem
from box8.ChatAgent import chat_doc, chat_enhance, chat_memorize
from box8.utils_pdf import PdfUtils

import markdown


"""
Naldia.async_mode = False

chat = Chatter()
# l'objet commun ne sert qu'à vérifier la présence d'une vectorisation antérieure, voir new_async_memorizer
memorizer = Memorizer()

# deprecated : async_memorize = sync_to_async(memorizer.memorize)
async_load = sync_to_async(chat.load)
async_ask = sync_to_async(chat.ask)
"""


"""résumer la fiche référence avec une proposition de localisation géographique dans un json selon le format : {"résumé" : résumé, lat : latitude, lng : longitude}. Ne retourner que le json"""
"""résumer la mission avec une proposition de localisation géographique dans un json selon le format : {"résumé" : résumé, lat : latitude, lng : longitude}"""

# FUNCTIONS
def get_absolute_path(relative_path):
    parts = relative_path.split('/')
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)
    return file_path

# USER VIEWS
@login_required
def chatapp_dashboard(request):
    # initialisation des variables session 
    chatapp_init_session(request)
    context = {
        "welcome": "Assistant d'analyse documentaire"
    }
    return render(request, 'chatapp/dashboard.html', context=context)

@login_required
def chatapp_webscrapping_demo(request):
    # initialisation des variables session 
    chatapp_init_session(request)
    context = {
        "welcome": "Collecteur de données externes"
    }
    return render(request, 'chatapp/webscrapping.html', context=context)


@login_required
def models_dashboard(request):
    # initialisation des variables session 
    chatapp_init_session(request)
    context = {
        "welcome": "Liste des modèles entrainés par Naldéo"
    }
    return render(request, 'chatapp/models_dashboard.html', context=context)


@login_required
def models_dpgf_demo(request):
    # initialisation des variables session 
    chatapp_init_session(request)
    context = {
        "welcome": "Economie de la construction"
    }
    return render(request, 'chatapp/models_dpgf.html', context=context)

@login_required
def models_vision_demo(request):
    # initialisation des variables session 
    chatapp_init_session(request)
    context = {
        "welcome": "Vision par ordinateur"
    }
    return render(request, 'chatapp/models_vision.html', context=context)




@login_required
def models_dpgf_demo_upload(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        uploaded_files = request.FILES.getlist('files')
        
        success_count = 0
        failure_count = 0
        datasetPath = os.path.join(get_absolute_path("sharepoint"), "datasets")

        for uploaded_file in uploaded_files:
            destination_path = os.path.join(datasetPath, uploaded_file.name)
            try:
                with open(destination_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                success_count += 1
            except Exception as e:
                failure_count += 1

        if success_count > 0:
            message = f'{success_count} fichiers téléchargés avec succès.'
        else:
            message = 'Échec du téléchargement des fichiers.'

        if failure_count > 0:
            message += f' {failure_count} fichiers n\'ont pas pu être téléchargés.'
            return JsonResponse({'message': 'Aucun fichier n\'a été téléchargé.'}, status=400)
        
        return JsonResponse({'message': 'Fichiers téléchargés.'})

    return JsonResponse({'message': 'Aucun fichier n\'a été téléchargé.'}, status=400)


@login_required
def models_dpgf_demo_train(request):
    data = json.loads(request.body.decode('utf-8'))
    modelName = data.get('model', '') # question posé
    
    datasetPath = os.path.join(get_absolute_path("sharepoint"), "datasets")
    response = "train_model(datasetPath, modelName)"
    """accuracy 
    contente = image base 64"""
    response["model"] = modelName
    response["state"] = "success"
    return JsonResponse(response)

@login_required
def models_dpgf_demo_ask(request):
    data = json.loads(request.body.decode('utf-8'))
    prompt = data.get('prompt', '') # question posée
    #model = DPGF(modelName="prix_prediction")
    prix = "model.ask(prompt)"
    response = {"content": prompt+" : " + str(prix),"state":"success"}
    return JsonResponse(response)


def chatapp_init_session(request):
    request.session['analyse_courante'] = ""
    request.session['fiches_selectionnees'] = []

def user_destination_dir(request):
    username = request.user.username if request.user.is_authenticated else 'visitor'
    destination_dir = os.path.join(get_absolute_path("sharepoint"), username)
    return destination_dir

@sync_to_async
def user_destination_dira(request):
    username = request.user.username if request.user.is_authenticated else 'visitor'
    destination_dir = os.path.join(get_absolute_path("sharepoint"), username)
    return destination_dir


def list_analyses(destination_dir,username):
    subdirectories = [d for d in os.listdir(destination_dir) if os.path.isdir(os.path.join(destination_dir, d)) and not d.startswith('_')]
    analyses_list = []
    if subdirectories:
        for i, caption in enumerate(subdirectories):
            analyses_dict = {"id": str(i + 1), "caption": caption, "type":"analyse", "parent_analyse":"", "memorized":True}
            analyses_list.append(analyses_dict)
        else:
            "pas de sous-répertoires"
    response_data={"username":username, "entries": analyses_list}
    return JsonResponse(response_data)


def list_analyse_files(destination_dir, analyse):
    files = os.listdir(destination_dir)
    file_list = []
    for i, caption in enumerate(files):
        # on évite les sous dossiers !
        file_path = os.path.join(destination_dir, caption)
        if os.path.isfile(file_path) and not (caption.endswith(".json") or caption.endswith(".txt")):
            file_dict = {"id": str(i + 1), "caption": caption, "type":"document", "parent_analyse":analyse}
            json_filename = caption + ".json"
            if os.path.isfile(os.path.join(destination_dir, json_filename)):
                file_dict["memorized"] = True
            else:
                # est-ce utile
                file_dict["memorized"] = True
            file_list.append(file_dict)
    response_data={"entries": file_list}
    return JsonResponse(response_data)



# REST JSON API

def chatapp_ajax_new_analyse(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            new_directory_name = data.get('analyse', '')
            user_dir = user_destination_dir(request)
            new_directory_path = os.path.join(user_dir, new_directory_name)

            if not new_directory_name:
                return JsonResponse({"error": "Le nom du répertoire ne peut pas être vide."}, status=400)

            if os.path.exists(new_directory_path):
                return JsonResponse({"error": "Le répertoire existe déjà."}, status=400)
            os.makedirs(new_directory_path)
            return list_analyses(user_dir,request.user.username) 
        except Exception as e:
            # Gérer les erreurs éventuelles ici
            return JsonResponse({"error": str(e)}, status=500)
    # Réponse en cas de méthode HTTP incorrecte
    return JsonResponse({"error": "Cette vue accepte uniquement les requêtes POST."}, status=405)


@login_required
def chatapp_upload(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        uploaded_files = request.FILES.getlist('files')
        analyse = request.POST.get('analyse')
        success_count = 0
        failure_count = 0
        for uploaded_file in uploaded_files:
            destination_dir = user_destination_dir(request)
            files_path = os.path.join(destination_dir, analyse)
            destination_path = os.path.join(files_path, uploaded_file.name)

            try:
                os.makedirs(destination_dir, exist_ok=True)
                with open(destination_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                success_count += 1
            except Exception as e:
                failure_count += 1

        if success_count > 0:
            message = f'{success_count} fichiers téléchargés avec succès.'
        else:
            message = 'Échec du téléchargement des fichiers.'

        if failure_count > 0:
            message += f' {failure_count} fichiers n\'ont pas pu être téléchargés.'
            return JsonResponse({'message': 'Aucun fichier n\'a été téléchargé.'}, status=400)
        return list_analyse_files(files_path, analyse)

    return JsonResponse({'message': 'Aucun fichier n\'a été téléchargé.'}, status=400)




"""fonction pour supprimer un répertoire récursivement """
def delete_directory_recursive(repertoire):
    try:
        # Supprimer tous les fichiers à l'intérieur du répertoire
        for element in os.listdir(repertoire):
            element_path = os.path.join(repertoire, element)
            if os.path.isfile(element_path):
                os.remove(element_path)
            elif os.path.isdir(element_path): # Si c'est un sous-répertoire, récursivement supprimer son contenu
                delete_directory_recursive(element_path)

        # Supprimer le répertoire lui-même
        os.rmdir(repertoire)
        print(f"Le répertoire {repertoire} et son contenu ont été supprimés avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


"""vue pour supprimer un répertoire d'analyse"""
def chatapp_ajax_delete_analyse(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        analyse=data["analyse"]
        user_dir = user_destination_dir(request)
        directory_to_delete = os.path.join(user_dir, analyse)
        delete_directory_recursive(directory_to_delete)
        return list_analyses(user_dir,request.user.username) 



"""retieve analyse folders for current user"""
def chatapp_ajax_analyses(request):
    if request.method == 'GET':
        chatapp_init_session(request)
        return list_analyses(user_destination_dir(request),request.user.username)  




"""set current analisys and retieve files for current user/analyse"""
def chatapp_ajax_set_analyse(request):
    if request.method == 'POST':
        analyse = request.POST.get('analyse', None)
        request.session['analyse_courante'] = analyse
        request.session['fiches_selectionnees'] = []
        destination_dir = os.path.join(user_destination_dir(request), analyse)
        return list_analyse_files(destination_dir,analyse)


"""fusion des pdf dans le dossier d'analyse"""
def chatapp_ajax_fusion_pdf(request):
    if request.method == 'POST':
        analyse = request.POST.get('analyse', None)
        request.session['analyse_courante'] = analyse
        destination_dir = os.path.join(user_destination_dir(request), analyse)
        PdfUtils.folder_fusion(destination_dir,"fusion.pdf")
        return list_analyse_files(destination_dir,analyse)


"""supprime un pdf du dossier d'analyse"""
def chatapp_delete_file(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        
        analyse = data.get('analyse', '')
        fiches = data.get('entries', '')
        destination_dir = os.path.join(user_destination_dir(request), analyse)
        delete_file_path = os.path.join(destination_dir,fiches[0])
        deletefile(delete_file_path)
        deletefile(delete_file_path+".json")
        deletefile(delete_file_path+".json.txt")
        return list_analyse_files(destination_dir,analyse)


def deletefile(path):
    if os.path.exists(path):
        try:
            os.remove(path)
            return True
        except Exception as e:
            print(f"Une erreur s'est produite lors de la suppression du fichier : {e}")
            return False
    else:
        return False

"""
met à jour les informations de session : non utilisé jusqu'à présent
"""
def chatapp_set_fiches(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['analyse_courante'] = data["analyse"]
        request.session['fiches_selectionnees'] = data["analyse"]
        return JsonResponse(data)


"""if 'current_fiches' not in request.session:
        response_data = {"content": "choisir un fichier avec lequel discutter"}
        return JsonResponse(response_data)"""


def build_talk_response(message,state):
    response_data = {"content": f"""{message}""","state":state}
    return response_data










#############################################################################
"""CHAT LLM FUNCTIONS """
#############################################################################


def chatapp_llm(request):
    if request.method == 'POST':
        # Récupérer le nom du LLM depuis la requête AJAX
        data = json.loads(request.body.decode('utf-8'))
        llm_name = data.get('name', 'openai')
        
        if llm_name == "debug":
            request.session['llm_debug'] = True
        else : 
            request.session['llm_debug'] = False
        # Mettre à jour la session avec le modèle de langage sélectionné
        request.session['selected_llm'] = llm_name
        

        # Retourner une réponse JSON pour l'interface utilisateur
        return JsonResponse({'status': 'success', 'message': f'LLM sélectionné : {llm_name}'})
    
    return JsonResponse({'status': 'error', 'message': 'Méthode HTTP non supportée'}, status=405)







# envoie une question sur le(s) documents sélectionnés (uniquement le premier en version demo, le mode multi-doc est à implémenter dans naldia)
# fait-on appel à des prompts préétablis ?

def chatapp_talk(request):
    destination_dir = user_destination_dir(request)
    data = json.loads(request.body.decode('utf-8'))
    analyse = data.get('analyse', '') # nom du dossier d'analyse
    entries = data.get('entries', '') # liste des documents sélectionnés pour la question 
    prompt = data.get('prompt', '') # question posée
    history = data.get('history', '') # historique de conversation
    llm = request.session.get('selected_llm', 'openai')
    print(llm)
    
    if request.session['llm_debug']:
        prompt = '\n\n'.join([lorem.paragraph() for _ in range(3)])
        response_data = build_talk_response(f"chatapp_talk : réponse à la question : {prompt}","warning")
        return JsonResponse(response_data)
    
    if not history:
        history=[]
    # print(history)
    
    # s'agit-t-il d'un prompt préenregistré et quel est le format de réponse attendu (json / texte, ...)
    awaited_result = special_prompts(prompt) 
    
    if len(entries)<1:
        response_data = build_talk_response("Attention, veuillez choisir le(s) documents avec lesquels vous souhaitez discuter","danger")
        return JsonResponse(response_data)
    
    # path vers le pdf analysé
    pdf=os.path.join(destination_dir,analyse,entries[0])
    
    if awaited_result["format"] == "text":
        response,history = chat_doc(pdf=pdf, question = awaited_result["prompt"], history = history, llm=llm)
        response_data = build_talk_response(response,"warning")
    
    elif awaited_result["format"] == "json":
        try:
            history=[]
            response, history = chat_doc(pdf=pdf, question = awaited_result["prompt"], history = history, llm=llm)
            #donnees_json = json.loads(response) # Analyser la chaîne JSON en un objet Python
            return JsonResponse(response) # on renvoie la réponse JsonResponse avec les données JSON

        except json.JSONDecodeError as e:
            # La chaîne n'est pas au format JSON valide
            return JsonResponse({'error': 'La chaîne n\'est pas au format JSON valide'}, status=400)
    return JsonResponse(response_data)











def chatapp_enhance(request):
    destination_dir = user_destination_dir(request)
    data = json.loads(request.body.decode('utf-8'))
    analyse = data.get('analyse', '') # nom du dossier d'analyse
    entries = data.get('entries', '') # liste des documents sélectionnés pour la question 
    prompt = data.get('prompt', '') # question posée
    history = data.get('history', '') # historique de conversation
    llm = request.session.get('selected_llm', 'openai')
    print(history)
    if request.session['llm_debug']:
        prompt = '\n\n'.join([lorem.paragraph() for _ in range(3)])
        response_data = build_talk_response(f"chatapp_enhance : réponse à la question : {prompt}","warning")
        return JsonResponse(response_data)
        
    
    if len(entries)<1:
        response_data = build_talk_response("Attention, veuillez choisir le(s) documents avec lesquels vous souhaitez discuter","danger")
        return JsonResponse(response_data)
    
    # path vers le pdf analysé
    pdf=os.path.join(destination_dir,analyse,entries[0])
    response = chat_enhance(pdf=pdf, question = prompt, history = history, llm=llm)
    response_data = build_talk_response(response,"warning")
    return JsonResponse(response_data)



from docx import Document
def generer_document_word(donnees, nom_fichier="document_genere.docx"):
    # Crée un nouveau document Word
    doc = Document()
    
    # Boucle à travers chaque entrée du tableau pour ajouter des chapitres
    for entree in donnees:
        titre, contenu = entree  # Décompose l'entrée en titre et contenu
        # Ajoute le titre comme un en-tête de niveau 1
        doc.add_heading(titre, level=1)
        # Ajoute le contenu comme un paragraphe
        doc.add_paragraph(contenu)
    # Enregistre le document avec le nom spécifié
    doc.save(nom_fichier)
    print(f"Document généré avec succès : {nom_fichier}")

def chatapp_word(request):
    destination_dir = user_destination_dir(request)
    data = json.loads(request.body.decode('utf-8'))
    analyse = data.get('analyse', '') # nom du dossier d'analyse
    entries = data.get('entries', '') # liste des documents sélectionnés pour la question 
    prompt = data.get('prompt', '') # question posée
    history = data.get('history', '') # historique de conversation
    llm = request.session.get('selected_llm', 'openai')
    if len(entries)<1:
        response_data = build_talk_response("Attention, veuillez choisir le(s) documents avec lesquels vous souhaitez discuter","danger")
        return JsonResponse(response_data)
    pdf=os.path.join(destination_dir,analyse,prompt)
    print(history)
    generer_document_word(history, f"{pdf}.docx")
    response_data = build_talk_response("Le word a été généré","info")
    return JsonResponse(response_data)





# todo => intégrer les prompts préétablis
# extraction GPS, Diagrammes circulaire, extraction sommaires et informations chiffrées ...
def special_prompts(prompt):
    if prompt.startswith("map_plot_"): 
        #extraire des informations de géolocalisation d'un document
        expectedformat="json"
    else:
        expectedformat="text"
    
    awaited_result = {"prompt":prompt,"format":expectedformat}
    return awaited_result


# todo => améliorer la présentation des réponses OpenAI
def format_text(text):
    return markdown.markdown(text)





# mémorize document (mode mulit-doc non implémenté)
def chatapp_memorize(request):
    destination_dir = user_destination_dir(request)
    data = json.loads(request.body.decode('utf-8'))
    analyse = data.get('analyse', '') # nom du dossier d'analyse
    entries = data.get('entries', '') # liste des documents sélectionnés pour la question 
    prompt = data.get('prompt', '') # question posée
    history = data.get('history', '') # historique de conversation
    llm = request.session.get('selected_llm', 'openai')

    print(llm)
    if request.session['llm_debug']:
        prompt = '\n\n'.join([lorem.paragraph() for _ in range(3)])
        response_data = build_talk_response(f"chatapp_memorize : réponse à la question : {prompt}","warning")
        return JsonResponse(response_data)

    if len(entries)<1:
        response_data = build_talk_response("Attention, veuillez choisir le(s) documents avec lesquels vous souhaitez discuter","danger")
        return JsonResponse(response_data)
    
    # path vers le pdf analysé
    pdf=os.path.join(destination_dir,analyse,entries[0])
    response = chat_memorize(pdf=pdf, question = prompt, history = history, llm=llm)
    response_data = build_talk_response(response,"warning")
    return JsonResponse(response_data)




# retour le cpntenu du ficher de vectorisation pour l'afficher dans le navigateur
def afficher_resume_vectorisation(request, analyse, nom_fichier):
    file_path = os.path.join(settings.BASE_DIR, 'chatapp','sharepoint', request.user.username, analyse, nom_fichier+".txt")
    # Vérifiez que le fichier existe avant de le renvoyer
    # printc(file_path,bcolors.FAIL)

    if os.path.exists(file_path):
        # Ouvrez le fichier PDF et renvoyez-le en tant que réponse HTTP
        with open(file_path, 'r', encoding='utf-8') as fichier:
            # Lire le contenu du fichier
            response_data = fichier.read()
        response_data = build_talk_response(format_text(response_data),"success")
        return JsonResponse(response_data)
    else:
        response_data = build_talk_response("le résumé du fichier n'existe pas, lancez la procédure","warning")
        return JsonResponse(response_data)





# non utilisé, permet de renvoyer le fichier sélectionner
def afficher_ressources(request, analyse, nom_fichier):
    file_path = os.path.join(settings.BASE_DIR, 'chatapp','sharepoint', request.user.username, analyse, nom_fichier)
    # Vérifiez que le fichier existe avant de le renvoyer
 
    if os.path.exists(file_path):
        # Ouvrez le fichier PDF et renvoyez-le en tant que réponse HTTP
        with open(file_path, 'rb') as f:
            response = FileResponse(f, as_attachment=True)
            return response
    else:
        # Gérez le cas où le fichier n'existe pas, par exemple, en renvoyant une erreur 404.
        from django.http import Http404
        raise Http404("Le fichier PDF n'existe pas.")