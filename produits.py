import requests
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Charger les variables du fichier .env
load_dotenv()

# Configuration Airtable
API_KEY = os.getenv("api_airtable")
BASE_ID = "appYkt1t8azfL3VJO"
TABLE_NAME = "code_barre"
TABLE_GESTION = "Gestion"
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
BASE_URL_GESTION = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_GESTION}"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def get_produit_info(produit_id):

    url = f"{BASE_URL}/{produit_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        record = response.json()
        fields = record.get("fields", {})

        # Assurez-vous que les champs existent et sont récupérés correctement
        nom_produit = fields.get("Nom", "Nom inconnu")
        categorie_produit = fields.get("Catégorie", "Catégorie inconnue")
        fournisseur_produit = fields.get("Fournisseur", "Fournisseur inconnu")
        qte_produit = fields.get("codeb_qte", "Qte inconnu")
        photo_produit = None
        if "Photo" in fields:
            attachments = fields["Photo"]
            if attachments:
                # Prendre la première image
                photo_produit = attachments[0].get("url", "Photo non disponible")

        return {
            "id": produit_id,  # Ajout de l'ID pour le tableau
            "nom": nom_produit,
            "categorie": categorie_produit,
            "fournisseur": fournisseur_produit,
            "qte": qte_produit,
            "photo": photo_produit,
        }
    else:
        print(f"Erreur {response.status_code} lors de la récupération du produit : {response.text}")
        return None

def add_record_to_airtable(produit_id):
    print(f"Tentative d'ajout du produit à Airtable : {produit_id}")
    produit_info = get_produit_info(produit_id)
    
    if not produit_info:
        print("Erreur : le produit n'a pas été trouvé dans la table `code_barre`.")
        return None  # Si le produit n'est pas trouvé, ne pas continuer
    
    # Préparer les données à envoyer à Airtable
    data = {
        "fields": {
            "Nom": produit_info["nom"],  # Ajoutez le nom du produit
            "Quantité": 1,  # Par défaut, une quantité de 1
        }
    }
    print(f"Données préparées pour Airtable : {data}")
    
    response = requests.post(BASE_URL, headers=HEADERS, json=data)

    if response.status_code == 200:
        created_record = response.json()
        print(f"Enregistrement créé avec succès dans Airtable : {created_record['id']}")
        return created_record['id']
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à Airtable : {response.text}")
        return None

def add_record_reduire_to_airtable_gestion(produit_id, qte_scan, emplacement, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Ajout du produit dans la table gestion : {produit_inf['nom']}, Quantité : -{qte_scan}")
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": "Réduire",
            "Référence" : "Scan",
            "Emplacement" : emplacement,
            "Qté Stock": -qte_scan,
            "Personne": username
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False

def reduire_camion_gestion(produit_id, qte_scan, emplacement, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Ajout du produit dans la table gestion : {produit_inf['nom']}, Quantité : -{qte_scan}")

    colonne_qte = f"Qté {emplacement}"
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": "Déplacer",
            "Référence" : "Scan",
            "Emplacement" : emplacement,
            colonne_qte: qte_scan,
            "Déplacer": True,
            "Personne": username
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False

def add_record_ajouter_to_airtable_gestion(produit_id, qte_scan, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Ajout du produit dans la table gestion : {produit_inf['nom']}, Quantité : {qte_scan}")
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": "Ajouter",
            "Référence" : "Scan",
            "Emplacement" : "STOCK",
            "Qté Stock": qte_scan,
            "Personne": username
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False


# Ton token d'authentification (récupéré dans Slack)
slack_token = os.getenv("slack_bot_token")

# Créer un client Slack
client = WebClient(token=slack_token)

# Identifiant du canal ou nom du canal (ex : '#general' ou 'C01ABCD2EFG')
franck_id = "U0612SGTKQW"
channel_stock = "G088J6KGFRR"


def envoie_msg_franck():

    try:
        # Envoi du message
        response = client.chat_postMessage(channel=franck_id, text="Une personne vient de scanner un code barre :)")
        print(f"Message envoyé : {response['message']['text']}")

    except SlackApiError as e:
        print(f"Erreur lors de l'envoi du message: {e.response['error']}")

def envoie_msg_stock(message):

    try:
        # Envoi du message
        response = client.chat_postMessage(channel=channel_stock, text=message)
        print(f"Message envoyé : {response['message']['text']}")

    except SlackApiError as e:
        print(f"Erreur lors de l'envoi du message: {e.response['error']}")
