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
                    chatapp_summarize, 
                    chatapp_file_to_rag,
                    chatapp_ajax_delete_analyse, 
                    chatapp_talk,
                    chatapp_enhance,
                    chatapp_get_conversation,
                    chatapp_save_conversation,
                    chatapp_delete_conversation_entry,
                    chatapp_word,
                    chatapp_sommaire,
                    chatapp_llm,
                    afficher_ressources, 
                    afficher_resume_vectorisation,
                    chatapp_ajax_fusion_pdf,
                    chatapp_delete_file,
                    chroma_reset,
                    models_dashboard, 
                    designer_agent_designer,
                    models_dpgf_demo,
                    models_dpgf_demo_upload,
                    models_dpgf_demo_train,
                    models_dpgf_demo_ask,
                    models_vision_demo,
                    chatapp_get_sharepoint_files,
                    designer_launch_crewai,
                    designer_list_json_files,
                    designer_get_diagram,
                    designer_save_diagram,
                    designer_delete_diagram,
                    designer_get_markdown_output,
                    designer_list_markdown_files,
                    designer_delete_markdown_file)

app_name="chatapp"
urlpatterns = [
    path('chatapp/', chatapp_dashboard, name="chatapp_dashboard"), # écran acceuil application chat documentaire
    path('chatapp/analyses/', chatapp_ajax_analyses, name="chatapp_ajax_analyses"), # retourne le json des analyses de l'utilisateur
    path('chatapp/new_analyses/', chatapp_ajax_new_analyse, name="chatapp_ajax_new_analyse"), # retourne le json des analyses de l'utilisateur
    path('chatapp/delete_analyses/', chatapp_ajax_delete_analyse, name="chatapp_ajax_delete_analyse"), # supprime le dossier d'analyses 
    path('chatapp/upload/', chatapp_upload, name='chatapp_upload'), # upload des fichiers dans le répertoire d'analyse courant
    path('chatapp/set_analyse/', chatapp_ajax_set_analyse, name="chatapp_ajax_set_analyse"), # définit de dossier d'analyse et retourne la liste des documents qu'il contient
    path('chatapp/set_fiche/', chatapp_set_fiches, name="chatapp_set_fiches"), # définit le dossier d'analyse et la liste des documents avec lesquels on va pouvoir chatter
    path('chatapp/memorize/', chatapp_summarize, name="chatapp_summarize"), # mémorise un document pour po
    path('chatapp/get_sharepoint_files/', chatapp_get_sharepoint_files, name="chatapp_get_sharepoint_files"), # get all files from user's SharePoint folder
    path('chatapp/rag_file/', chatapp_file_to_rag, name="chatapp_file_to_rag"), # définit le dossier d'analyse et la liste des documents avec lesquels on va pouvoir chatter
     
    path('chatapp/talk/', chatapp_talk, name="chatapp_talk"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/enhance/', chatapp_enhance, name="chatapp_enhance"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    
    path('chatapp/get_conversation/', chatapp_get_conversation, name="chatapp_get_conversation"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/save_conversation/', chatapp_save_conversation, name="chatapp_save_conversation"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    
    
    path('chatapp/delete_entry/', chatapp_delete_conversation_entry, name="chatapp_delete_conversation_entry"), # efface l'entrée donnée 
    
    path('chatapp/word/', chatapp_word, name="chatapp_word"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/sommaire/', chatapp_sommaire, name="chatapp_sommaire"), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    
    path('chatapp/llm/', chatapp_llm, name="chatapp_llm"), # permet de choisir le LLM
    
    path('chatapp/info/<str:analyse>/<str:nom_fichier>', afficher_resume_vectorisation, name='afficher_resume_vectorisation'), # retourne le résumé de la  vectorisé du document mémorisé
    path('chatapp/fusion/', chatapp_ajax_fusion_pdf, name="chatapp_ajax_fusion_pdf"), # fusionne les pdf du répertoire
    path('chatapp/delete_doc/', chatapp_delete_file, name="chatapp_delete_file"), # fusionne les pdf du répertoire
    
    path('chatapp/chroma_reset/', chroma_reset, name="chroma_reset"), # chroma_reset la vector db 
    
    path('chatapp/designer', designer_agent_designer, name="agent_designer"), # demo application webscrapping
    path('chatapp/designer/json-files/', designer_list_json_files, name='list_json_files'),
    path('chatapp/designer/json-files/<str:filename>/', designer_get_diagram, name='designer_get_diagram'),
    path('chatapp/designer/save-diagram/', designer_save_diagram, name='save_diagram'), # envoi une question sur le document mémorisé en cours (multi document non implémenté)
    path('chatapp/designer/delete-diagram/<str:filename>/', designer_delete_diagram, name='delete_diagram'),
    path('chatapp/designer/get_markdown_output/', designer_get_markdown_output, name='get_markdown_output'),
    path('chatapp/designer/list_markdown_files/', designer_list_markdown_files, name='list_markdown_files'),
    path('chatapp/designer/launch_crewai/', designer_launch_crewai, name='designer_launch_crewai'),
    path('chatapp/designer/delete-markdown-file/', designer_delete_markdown_file, name='designer_delete_markdown_file'),
    
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