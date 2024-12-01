import os
import re
import shutil
from PyPDF2 import PdfWriter

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