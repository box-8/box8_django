from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

#from Naldea.views import index
from .views import (chatapp_dashboard,
                    chatapp_ajax_analyses, 
                    chatapp_ajax_set_analyse,
                    chatapp_set_fiches, 
                    chatapp_upload, 
                    chatapp_ajax_new_analyse,
                    chatapp_memorize, 
                    chatapp_file_to_rag,
                    chatapp_ajax_delete_analyse, 
                    chatapp_talk,
                    chatapp_enhance,
                    chatapp_word,
                    chatapp_sommaire,
                    chatapp_llm,
                    afficher_ressources, 
                    afficher_resume_vectorisation,
                    chatapp_ajax_fusion_pdf,
                    chatapp_delete_file,
                    chroma_reset,
                    models_dashboard, 
                    chatapp_webscrapping_demo,
                    models_dpgf_demo,
                    models_dpgf_demo_upload,
                    models_dpgf_demo_train,
                    models_dpgf_demo_ask,
                    models_vision_demo)

app_name="chatapp"
urlpatterns = [
    path('chatapp/', chatapp_dashboard, name="chatapp_dashboard"), # écran acceuil application chat documentaire
    path('chatapp/analyses/', chatapp_ajax_analyses, name="chatapp_ajax_analyses"), # retourne le json des analyses de l'utilisateur
    path('chatapp/new_analyses/', chatapp_ajax_new_analyse, name="chatapp_ajax_new_analyse"), # retourne le json des analyses de l'utilisateur
    path('chatapp/delete_analyses/', chatapp_ajax_delete_analyse, name="chatapp_ajax_delete_analyse"), # supprime le dossier d'analyses 
    path('chatapp/upload/', chatapp_upload, name='chatapp_upload'), # upload des fichiers dans le répertoire d'analyse courant
    path('chatapp/set_analyse/', chatapp_ajax_set_analyse, name="chatapp_ajax_set_analyse"), # définit de dossier d'analyse et retourne la liste des documents qu'il contient
    path('chatapp/set_fiche/', chatapp_set_fiches, name="chatapp_set_fiches"), # définit le dossier d'analyse et la liste des documents avec lesquels on va pouvoir chatter
    path('chatapp/memorize/', chatapp_memorize, name="chatapp_memorize"), # mémorise un document pour pouvoir chatter avec 
    path('chatapp/rag_file/', chatapp_file_to_rag, name="chatapp_file_to_rag"), # définit le dossier d'analyse et la liste des documents avec lesquels on va pouvoir chatter
    
    path('chatapp/talk/', chatapp_talk, name="chatapp_talk"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/enhance/', chatapp_enhance, name="chatapp_enhance"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/word/', chatapp_word, name="chatapp_word"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/sommaire/', chatapp_sommaire, name="chatapp_sommaire"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    
    path('chatapp/llm/', chatapp_llm, name="chatapp_llm"), # permet de choisir le LLM
    
    path('chatapp/info/<str:analyse>/<str:nom_fichier>', afficher_resume_vectorisation, name='afficher_resume_vectorisation'), # retourne le résumé de la  vectorisé du document mémorisé
    path('chatapp/fusion/', chatapp_ajax_fusion_pdf, name="chatapp_ajax_fusion_pdf"), # fusionne les pdf du répertoire
    path('chatapp/delete_doc/', chatapp_delete_file, name="chatapp_delete_file"), # fusionne les pdf du répertoire
    
    path('chatapp/chroma_reset/', chroma_reset, name="chroma_reset"), # chroma_reset la vector db 
    
    path('chatapp/webscrapping', chatapp_webscrapping_demo, name="chatapp_webscrapping_demo"), # demo application webscrapping


    path('models/', models_dashboard, name="models_dashboard"), # écran acceuil models
    path('models/dpgf', models_dpgf_demo, name="models_dpgf_demo"), # demo application 
    path('models/dpgf/upload', models_dpgf_demo_upload, name="models_dpgf_demo_upload"), # demo application 
    path('models/dpgf/ask', models_dpgf_demo_ask, name="models_dpgf_demo_ask"), # demo application 
    path('models/dpgf/train', models_dpgf_demo_train, name="models_dpgf_demo_train"), # demo application 


    path('models/vision', models_vision_demo, name="models_vision_demo"), # demo application 
    

    # path('chatapp/ressources/<str:analyse>/<str:nom_fichier>', afficher_ressources, name='afficher_ressources'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)