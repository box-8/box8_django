import os
from matplotlib import pyplot as plt
import joblib
from transformers import pipeline


def printI(str):
    print()
    print("\033[93m"+str+"\033[0m")
    print()

def printB(str):
    print()
    print("\033[94m"+str+"\033[0m")
    print()


joblib_backups = "C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\v0\\auth\\chatapp\\sharepoint\\models\\"
repertoire_courant = os.getcwd()

print(repertoire_courant)



from transformers import AutoModelForCausalLM, AutoTokenizer as Tokenizer
from PIL import Image



class StdModel():
    def __init__(self, task="text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment"):
        self.task = task
        self.model = model
        # chemin de sauvegarde du pipeline dans un répertoire spécifique
        self.chemin_sauvegarde = joblib_backups+self.__class__.__name__+".joblib"
        self.result = None
        self.load()
    
    def load(self):
        # Chargement du pipeline depuis le fichier
        try:
            # Chargement du pipeline depuis le fichier
            self.pipeline = joblib.load(self.chemin_sauvegarde)
        except FileNotFoundError:
            # Si le fichier n'est pas trouvé, créez un nouveau pipeline
            # Sauvegarde du nouveau pipeline
            printI("Sauvegarde du pipeline pour le transformer "+self.__class__.__name__)
            self.dump()

    def dump(self):
        self.pipeline = pipeline(self.task, self.model)
        joblib.dump(self.pipeline, self.chemin_sauvegarde)
        return self.pipeline

    def do(self,text="J'aime beaucoup la soupe miso!"):
        # Exemple d'analyse de sentiment
        return self.pipeline(text)
    
    def forget(self):
        if os.path.exists(self.chemin_sauvegarde):
            os.remove(self.chemin_sauvegarde)
            print(f"Le modèle {self.chemin_sauvegarde} a été supprimé avec succès.")
        else:
            print(f"Le modèle {self.chemin_sauvegarde} n'existe pas.")
        

class MoonDream(StdModel):
    def __init__(self, image=""):
        self.task = "text-generation"
        self.model_name_or_path = "vikhyatk/moondream1"  # Identifiant du modèle
        # self.chemin_sauvegarde = os.path.join(joblib_backups, self.__class__.__name__+".joblib")
        self.chemin_sauvegarde = joblib_backups+self.__class__.__name__+".joblib"
        self.result = None
        self.load()  # Charge le modèle et le tokenizer lors de l'initialisation
        if image:
            self.image(image)

    def dump(self):
        # Charge le modèle et le tokenizer
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path, trust_remote_code=True)
        self.tokenizer = Tokenizer.from_pretrained(self.model_name_or_path)
        
        # Sauvegarde le modèle et le tokenizer dans chemin_sauvegarde
        joblib.dump((self.model, self.tokenizer), self.chemin_sauvegarde)

    def load(self):
        """Charge le modèle et le tokenizer depuis un fichier joblib si disponible."""
        if os.path.exists(self.chemin_sauvegarde):
            # Charge le modèle et le tokenizer sauvegardés
            self.model, self.tokenizer = joblib.load(self.chemin_sauvegarde)
        else:
            # Si aucun fichier de sauvegarde, charge depuis l'identifiant du modèle et sauvegarde
            self.dump()

    def image(self,image_path):
        self.image = Image.open(image_path)
        self.enc_image = self.model.encode_image(self.image)
    
    def do(self, q):
        self.result = self.model.answer_question(self.enc_image, q, self.tokenizer)
        print(self.result)
        return self.result




###########################################################################################
#
#   Classes Métier Heritant de StdModel
#
###########################################################################################



class TraductionOrale(StdModel):
    def __init__(self):
        super().__init__("automatic-speech-recognition", "facebook/seamless-m4t-v2-large")

class SentimentModel(StdModel):
    def __init__(self):
        super().__init__("text-classification", "nlptown/bert-base-multilingual-uncased-sentiment")

class TraductionModel(StdModel):
    def __init__(self):
        # Pipeline pour la traduction (Anglais vers Français par exemple)
        super().__init__("translation_en_to_fr", "t5-base")
        
class ZeroShotModel(StdModel):
    def __init__(self,labels):
        self.labels = labels
        super().__init__("zero-shot-classification", "facebook/bart-large-mnli")

    def do(self,text):
        print("Analyse "+ self.task +"...")
        self.result = self.pipeline(
            text,
            self.labels,
            hypothesis_template="Cet article est sur {}."
        )
        return self.result

    def plot(self):
        plt.figure(figsize=(8, 6))
        plt.barh(self.result['labels'], self.result['scores'], color='skyblue')
        plt.xlabel('Scores')
        plt.title('Scores pour chaque catégorie')
        chemin_fichier = joblib_backups + 'ZeroShotModel.png'
        plt.savefig(chemin_fichier)
        plt.show()


class ResumeModel(StdModel):
    def __init__(self):
        super().__init__("summarization", "facebook/bart-large-cnn")
    def do(self,text):
        self.result = self.pipeline(text, max_length=50, min_length=30, do_sample=False)
        return self.result
    

class ImageDescriber(StdModel):
    def __init__(self):
        super().__init__("image-to-text", "Sof22/image-caption-large-copy")
    def do(self,image):
        self.result = self.pipeline(image)
        return self.result

# manque OCR
class QuestionImage(StdModel):
    def __init__(self):
        super().__init__("document-question-answering", "jinhybr/OCR-DocVQA-Donut")
    def do(self,image,q):
        self.result = self.pipeline(image,q)
        return self.result


class ImageSegmentation(StdModel):
    def __init__(self):
        super().__init__("image-segmentation", "nvidia/segformer-b5-finetuned-ade-640-640")
    def do(self,image):
        self.result = self.pipeline(image)
        return self.result
    def plot(self):
        plt.figure(figsize=(8, 6))
        plt.barh(self.result['label'], self.result['score'], color='skyblue')
        plt.xlabel('Scores')
        plt.title('Scores pour chaque catégorie')
        chemin_fichier = joblib_backups + 'castle.png'
        plt.savefig(chemin_fichier)
        plt.show()



class Mixtral(StdModel):
    def __init__(self):
        super().__init__("text-generation", "mistralai/Mistral-7B-v0.1")

    def do(self,text):
        self.result = self.pipeline(text)
        return self.result



#######################################################
def notesdeefrais():
    # Chemin du répertoire contenant les images
    mes_notes_de_frais = "C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\v0\\auth\\chatapp\\sharepoint\\gael.jaunin\\notes de frais\\"

    # Création d'une instance de QuestionImage
    Questionneur = QuestionImage()
    q = "What is the invoice price?"

    # Liste des fichiers dans le répertoire
    fichiers_images = [f for f in os.listdir(mes_notes_de_frais) if f.endswith(".png")]
    # Boucle pour traiter chaque image
    for fichier_image in fichiers_images:
        print(fichier_image)
        # Chemin complet de l'image
        chemin_image = os.path.join(mes_notes_de_frais, fichier_image)
        # Appliquer QuestionImage.do à chaque image
        resultat = Questionneur.do(chemin_image, q)
        # Afficher la réponse pour chaque image
        print(resultat[0]['answer'])


def moon():
    imagepath = "C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\v0\\auth\\chatapp\\sharepoint\\gael.jaunin\\notes de frais\\resto-jour-1.png"
    loop = True
    while loop:
        q = input("votre question (e pour quiter) : ")
        if q == "e":
            loop = False
        else:
            print(q)
            Questionneur = MoonDream(imagepath)
            response = Questionneur.do(q)
            printB(response[0]['summary_text'])

def chatbot():
    loop = True
    while loop:
        q = input("votre question (e pour quiter) : ")
        
        if q == "e":
            loop = False
        else:
            print(q)
            Questionneur = Mixtral()
            response = Questionneur.do(q)
            printB(response[0]['summary_text'])


def traduct():
    loop = True
    while loop:
        q = input("The text to translate (e pour quiter) : ")
        
        if q == "e":
            loop = False
        else:
            print(q)
            Traducteur = TraductionModel()
            traduction = Traducteur.do(text)[0]['translation_text']
            printB(traduction)

i= input("""
    0 : chat bot mistral AI 
    1 : etude de texte
    2 : notes de frais
    3 : image processing
    4 : image questionning
votre choix : """)


if i=="0":
    chatbot()

if i=="4":
    moon()

if i=="2":
    notesdeefrais()

#######################################################



# Exemple de texte long à résumer
if i=="1":
        
    text = """
    The document is a public service delegation contract for drinking water. It includes several chapters that cover general provisions, rights and obligations of the delegatee, resources allocated to the delegation, delegatee's responsibility and insurance, preparation period for the service, water resource and production, as well as safety measures and water quality monitoring.

    The document provides information on the monitoring, operation, maintenance of drinking water production facilities, management of green spaces, handling of liquid discharges, bulk water delivery and importation, right of use of public roads and private properties, regime of pipelines under public roads, distributed water quality, network purging operations, relations with third parties, connection regulations, network accessories, and fire hydrants, water theft prevention, and general conditions of water supply to subscribers. The document fragment pertains to the management of subscribers to public sanitation services, customer reception, expected service performance for users, management of subscribers in difficulty, perceived quality measurement, meter regulations, communication and visibility of the service, works regulations, environmental aspects, and the information system. The document fragment covers various articles related to the management of the public drinking water service.
    """

    print(f"Texte original en anglais : ", text)

    Resumeur = ResumeModel()
    summary = Resumeur.do(text)
    printB(summary[0]['summary_text'])

    

    Traducteur = TraductionModel()
    traduction = Traducteur.do(text)[0]['translation_text']
    printI(f"Texte traduit en français via le modèle : {Traducteur.model}")
    printB(traduction)


    labels=[
    "Eau potable",
    "Assainissement",
    "Voirie Réseaux",
    "Chauffage urbain",
    "Energie Photovoltaique",
    "Informatique"
    ]

    print ("Liste des catégories de texte : ", labels)
    Classificateur = ZeroShotModel(labels)
    result = Classificateur.do(traduction)
    printI("affichage du type de contenu")
    Classificateur.plot()


    image_path = joblib_backups + 'ZeroShotModel.png'
    ImageComenteur = ImageDescriber()
    result = ImageComenteur.do(image_path)
    print(result[0]['generated_text'])


if i=="3":
    url = joblib_backups + 'castle.jpg'
    imageReader = ImageSegmentation()
    result = imageReader.do(url)
    printI("affichage du type de contenu")
    imageReader.plot()