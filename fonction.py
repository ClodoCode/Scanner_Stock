import json

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