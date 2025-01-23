import json
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
TABLE_PRODUIT = "Produits"
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
BASE_URL_GESTION = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_GESTION}"
BASE_URL_PRODUIT = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_PRODUIT}"
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

def add_record_ajouter_to_airtable_gestion(produit_id, qte_scan, username, societe):
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
            "Personne": username,
            "Societe": societe
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False


def plus_list_prod(produit_id, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Ajout du produit dans la table gestion : {produit_inf['nom']}, Quantité : 1")
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": "Ajouter",
            "Référence" : "Ajout Rapide",
            "Emplacement" : "STOCK",
            "Qté Stock": 1,
            "Personne": username,
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False


def moins_list_prod(produit_id, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Ajout du produit dans la table gestion : {produit_inf['nom']}, Quantité : 1")
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": "Réduire",
            "Référence" : "Sortie Rapide",
            "Emplacement" : "STOCK",
            "Qté Stock": -1,
            "Personne": username,
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False

def list_produit_rea():

    url = f"{BASE_URL_PRODUIT}"
    params = {"view": "rea"}
    response = requests.get(url, headers=HEADERS, params=params)

    
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])  # Liste des enregistrements

        # Construire une liste des produits
        produits = []
        for record in records:
            fields = record.get("fields", {})  # Récupérer les champs du produit

            produit = {
                "nom": fields.get("Nom", "Nom inconnu"),
                "categorie": fields.get("Catégorie", "Catégorie inconnue"),
                "fournisseur": fields.get("Fournisseur", "Fournisseur inconnu"),
                "qte": fields.get("Qté Stock (Réel)", "Qte inconnue"),
            }
            produits.append(produit)

        return produits
    else:
        print(f"Erreur {response.status_code} : {response.text}")
        return None


def list_produit():

    url = f"{BASE_URL_PRODUIT}"
    params = {"view": "Favoris"}
    response = requests.get(url, headers=HEADERS, params=params)

    
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])  # Liste des enregistrements

        # Construire une liste des produits
        produits = []
        for record in records:
            fields = record.get("fields", {})  # Récupérer les champs du produit

            produit = {
                "nom": fields.get("Nom", "Nom inconnu"),
                "categorie": fields.get("Catégorie", "Catégorie inconnue"),
                "fournisseur": fields.get("Fournisseur", "Fournisseur inconnu"),
                "qte": fields.get("Qté Stock (Réel)", "Qte inconnue"),
                "id": fields.get("TheId", "ID inconnue"),
            }
            produits.append(produit)

        return produits
    else:
        print(f"Erreur {response.status_code} : {response.text}")
        return None



# FONCTION POUR SLACK


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





# Fonction pour charger les utilisateurs depuis un fichier JSON
def load_users_from_json(file_path):
    """Charge les utilisateurs à partir d'un fichier JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            users = json.load(file)
            # Vérification de la structure du fichier JSON
            for user_id, user_data in users.items():
                if "nom" not in user_data or "role" not in user_data:
                    print(f"Erreur : Format JSON incorrect pour l'utilisateur {user_id}.")
                    return {}
            print("Utilisateurs chargés :", users)  # Affichage pour débogage
            return users
    except FileNotFoundError:
        print(f"Erreur : Fichier '{file_path}' non trouvé.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Erreur de format JSON : {e}")
        return {}
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        return {}