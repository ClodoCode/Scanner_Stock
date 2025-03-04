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
TABLE_COMMAND = "Commandes"
TABLE_CONF_COMMAND = "Conf Cde"
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
BASE_URL_GESTION = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_GESTION}"
BASE_URL_PRODUIT = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_PRODUIT}"
BASE_URL_COMMAND = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_COMMAND}"
BASE_URL_CONF_COMMAND = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_CONF_COMMAND}"
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

        # Récupérer la photo
        photos = fields.get("Photo", [])
        photo_url = photos[0]["url"] if photos else None 

        return {
            "id": produit_id,  # Ajout de l'ID pour le tableau
            "nom": nom_produit,
            "categorie": categorie_produit,
            "fournisseur": fournisseur_produit,
            "qte": qte_produit,
            "photo": photo_url,
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

def add_recption_cde(produit_id, qte):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Ajout du produit dans la table gestion : {produit_inf['nom']}, Quantité : {qte}")
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": "Ajouter",
            "Référence" : "Reception commande",
            "Emplacement" : "STOCK",
            "Qté Stock": qte,
        }
    }

    response = requests.post(BASE_URL_GESTION, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table gestion.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False

def mov_prod(produit_id, action, ref, qte, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Action": action,
            "Référence" : ref,
            "Emplacement" : "STOCK",
            "Qté Stock": qte,
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
    produits = []
    offset = None  # Variable pour stocker l'offset

    while True:
        if offset:
            params["offset"] = offset  # Ajouter l'offset si présent

        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])  # Liste des enregistrements

            for record in records:
                fields = record.get("fields", {})

                produit = {
                    "nom": fields.get("Nom", "Nom inconnu"),
                    "ref": fields.get("Référence", "Référence inconnue"),
                    "categorie": fields.get("Catégorie", "Catégorie inconnue"),
                    "fournisseur": fields.get("Fournisseur", "Fournisseur inconnu"),
                    "qte": fields.get("Qté Stock (Réel)", "Qte inconnue"),
                    "id": fields.get("TheId", "ID inconnue"),
                    "prix": fields.get("Prix Unitaire", "Pas de prix"),
                    "lieu": fields.get("Lieu", "Lieu inconnue"),
                    "mini": fields.get("Minimum", "Pas de minimum"),
                    "max": fields.get("Maximum", "Pas de maximum"),
                    "photo": fields.get("Photo", [{}])[0].get("url", None),

                }
                produits.append(produit)

            # Vérifier s'il y a une pagination
            offset = data.get("offset")
            if not offset:  # Si plus d'offset, on sort de la boucle
                break
        else:
            print(f"Erreur {response.status_code} : {response.text}")
            return None

    return produits

def list_command():

    url = f"{BASE_URL_COMMAND}"
    params = {"view": "Command scan"}
    response = requests.get(url, headers=HEADERS, params=params)

    
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])  # Liste des enregistrements

        # Construire une liste des produits
        commands = []
        for record in records:
            fields = record.get("fields", {})  # Récupérer les champs du produit

            command = {
                "Num cde": fields.get("Nom cde", "Nom inconnu"),
                "Produits": fields.get("Produits", "Produits inconnue"),
                "ref": fields.get("Référence", "Référence inconnue"),
                "fournisseur": fields.get("Fournisseur", "Fournisseur inconnue"),
                "id": fields.get("id", "id inconnue"),
                "status": fields.get("Status", "Status inconnue"),
                "qte_command": fields.get("Qte Cde", "Qte Cde inconnue"),
                "qte_recu": fields.get("Qté reçus", "Qté reçus inconnue"),
            }
            commands.append(command)

        return commands
    else:
        print(f"Erreur {response.status_code} : {response.text}")
        return None




def crea_command(produit_id, qte_cde, username):
    """Ajoute un enregistrement dans la table gestion."""
    produit_inf = get_produit_info(produit_id)
    print(f"Création commande pour : {produit_inf['nom']}, Quantité : {qte_cde}")
    
    data = {
        "fields": {
            "Produits": [produit_id],
            "Référence" : "Cde Rapide",
            "Status" : "Incomplète",
            "Qte Cde":qte_cde,
            "Personne": username,
        }
    }

    response = requests.post(BASE_URL_COMMAND, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Enregistrement créé avec succès dans la table commande.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de l'ajout à la table gestion : {response.text}")
        return False


def cree_prod(nom, ref, categorie, fourn, lieu, qte, prix, mini, max):
    """Ajoute un enregistrement dans la table gestion."""
    print(f"Création du produit : {nom}")
    
    data = {
        "fields": {
            "Nom": nom,
            "Référence": ref,
            "Catégorie": categorie,
            "Fournisseur": fourn,
            "Lieu": lieu,
            "Qté Stock": qte,
            "Prix Unitaire": prix,
            "Favoris": True,
            "Minimum": mini,
            "Maximum": max,
        }
    }

    response = requests.post(BASE_URL_PRODUIT, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Produit créé avec succés.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de la création du produit : {response.text}")
        return False

def update_product(produit_id, updated_data):
    """Met à jour un produit dans Airtable avec gestion des erreurs."""

    url = f"{BASE_URL}/{produit_id}"
    data = {"fields": updated_data}

    try:
        response = requests.patch(url, json=data, headers=HEADERS)
        response_data = response.json()

        if response.status_code == 200:
            print(f"✅ Mise à jour réussie pour {produit_id}")
            return response_data  # ✅ Retourne les données mises à jour
        else:
            print(f"❌ Erreur lors de la mise à jour d'Airtable : {response.status_code} - {response.text}")
            return None  # ❌ Retourne None en cas d'échec

    except requests.RequestException as e:
        print(f"❌ Erreur réseau : {e}")
        return None  # ❌ Retourne None en cas d'erreur réseau


def confirm_command(id_command, qte):
    
    data = {
        "fields": {
            "Commande": [id_command],
            "Action": "Réception",
            "Qté reçus": qte,
        }
    }

    response = requests.post(BASE_URL_CONF_COMMAND, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("Commande réceptionné avec succès.")
        return True
    else:
        print(f"Erreur {response.status_code} lors de la reception de la commande : {response.text}")
        return False


# FONCTION POUR SLACK


# Ton token d'authentification (récupéré dans Slack)
slack_token = os.getenv("slack_bot_token")

# Créer un client Slack
client = WebClient(token=slack_token)

# Identifiant du canal ou nom du canal (ex : '#general' ou 'C01ABCD2EFG')
franck_id = "U0612SGTKQW"
channel_stock = "G088J6KGFRR"
channel_cde = "C08AMGL9ZAL"


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

def envoie_msg_command(message):

    try:
        # Envoi du message
        response = client.chat_postMessage(channel=channel_cde, text=message)
        print(f"Message envoyé : {response['message']['text']}")

    except SlackApiError as e:
        print(f"Erreur lors de l'envoi du message: {e.response['error']}")

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
            print("Utilisateurs chargés")  # Affichage pour débogage
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