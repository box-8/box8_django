import os
import re
import shutil
import PyPDF2
from PyPDF2 import PdfWriter
from docx import Document


def extractPageTextFromFile(src):
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



class PdfUtils:
    # fusionne les pdf de la liste dans un pdf enregistré dans fusion_path
    def __fusion_from_list(fusion_path, liste_pdfs):
        try:
            fusionneur = PdfWriter()
            # Ajouter les fichiers PDF à fusionner
            for pdf_path in liste_pdfs:
                fusionneur.append(pdf_path)
            # Fusionner les fichiers enregistrés dans un nouveau PDF
            fusionneur.write(fusion_path)
            fusionneur.close()
        except Exception as e:
            print("Une erreur s'est produite lors de la fusion des PDF :" +  str(e))
    
    # fusionne les fichiers pdf dans le répertoire donné avec le nom souhaité
    def folder_fusion(folder_path, fusion_name="fusion.pdf"):
        liste_pdfs = []
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                    filepath = os.path.join(folder_path, filename)
                    if filename ==fusion_name :
                        print("  >>> Fichier de fusion préexistant")
                        continue
                    if filename.endswith(".pdf"):
                        liste_pdfs.append(filepath)
            nombre_pdf = len(liste_pdfs)
            if nombre_pdf >1: # on fusionne
                dest_file = os.path.join(folder_path,fusion_name)
                PdfUtils.__fusion_from_list(dest_file, liste_pdfs)
                print(f"  >>> le fichier de fusion a été créée ({nombre_pdf} pdf)")
            elif nombre_pdf ==1: # on crée une copie avec le nom fusion.pdf
                dest_file = os.path.join(folder_path,fusion_name)
                shutil.copy(liste_pdfs[0], dest_file)
                print(f"  >>> le fichier de copie a été créé")
            else:
                print(f"  >>>  pas de fichier à fusionner")


    # deprecated : extrait les json dans du texte
    def extract_json(text):
        pattern = r"\{(.*?)\}"
        matches = re.findall(pattern, text)
        return matches