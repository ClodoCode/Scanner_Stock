from customtkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from tkinter.font import Font
from fonction import get_produit_info, add_record_ajouter_to_airtable_gestion, envoie_msg_stock


def show_entree(main_view):
    """Affiche la page Sortie."""
    # Effacer le contenu existant dans main_view
    for widget in main_view.winfo_children():
        widget.destroy()

    # Créer un cadre principal pour cette page
    tab_entree = CTkFrame(master=main_view, fg_color="#f7f7f7")
    tab_entree.pack(expand=True, fill="both")

    # Titre de la section
    title_label = CTkLabel(
        tab_entree,
        text="Faire des entrées de Stock",
        font=("Arial", 35, "bold"),
        text_color="#333",
        anchor="center",
        fg_color="#f7f7f7"
    )
    title_label.pack(pady=(10, 5))

    # Instructions pour l'utilisateur
    instructions_label = CTkLabel(
        tab_entree,
        text=(
            "1. Scannez un produit pour augmenter sa quantité en stock.\n"
            "2. Si vous avez scanné un produit par erreur, scannez le code-barres SUPP001, "
            "puis le produit à supprimer.\n"
            "3. Une fois tous les produits scannés, utilisez CONFIRM001 pour valider les changements."
        ),
        font=("Arial", 18),
        text_color="#555",
        anchor="w",
        fg_color="#f7f7f7",
        wraplength=1100
    )
    instructions_label.pack(pady=(5, 15))

    # Créer un cadre scrollable pour le tableau avec un fond blanc
    scrollable_frame = CTkScrollableFrame(tab_entree, width=1100, height=500, fg_color="white")
    scrollable_frame.pack(padx=15, pady=(0, 10))

    # Noms des colonnes
    columns = ["Nom", "Fournisseur", "Quantité Stock", "Quantité Scannée"]

    # Définir les largeurs des colonnes
    column_widths = {
        "Nom": 550,
        "Fournisseur": 150,
        "Quantité Stock": 80,
        "Quantité Scannée": 80,
    }

    # Ajouter les en-têtes des colonnes
    header_frame = CTkFrame(scrollable_frame, fg_color="#2A8C55")
    header_frame.pack(fill="x", pady=0)

    for col in columns:
        # Définir padx_value en fonction de la colonne
        if col == "Quantité Scannée":
            padx_value = 100  # Décalage spécifique pour "Quantité Scannée"
        else:
            padx_value = 0  # Pas de décalage pour les autres colonnes

        # Créer les en-têtes des colonnes
        header_label = CTkLabel(
            header_frame,
            text=col,
            width=column_widths[col],
            font=("Arial", 18, "bold"),
            text_color="#fff",
            fg_color="#2A8C55",
            anchor="center",
            padx=padx_value  # Appliquer le décalage pour chaque colonne
        )
        header_label.pack(side="left", padx=(5, 5))  # Ajouter un léger padding horizontal entre les colonnes

    # Données de tableau (initialement vide)
    table_data = []

    # Ajouter les lignes de données dans le tableau
    row_font = Font(family="Arial", size=12)

    for row in table_data:
        row_frame = CTkFrame(scrollable_frame, fg_color="#f7f7f7")
        row_frame.pack(fill="x", pady=0)

        for i, item in enumerate(row):
            entry = CTkEntry(
                row_frame,
                width=column_widths[columns[i]],  # Utiliser la largeur de la colonne pour chaque entrée
                state="normal",
                justify="center",
                fg_color="#f7f7f7",
                font=("Arial", 18),
                border_width=0,
                text_color="#333",
            )
            entry.insert(0, item)
            entry.pack(side="left", padx=(5, 5))  # Ajouter un léger padding horizontal entre les colonnes

    global tree_ajouter, label_status, label_status_societe
    tree_ajouter = scrollable_frame

    label_status = CTkLabel(
        tab_entree,
        text="",
        font=("Arial", 18, "italic"),
        text_color="green",
        fg_color="#f7f7f7"
    )
    label_status.pack(pady=(5, 15))


    button_conf = CTkButton(master=tab_entree, text="Confirmer", font=("Arial Bold", 17), command=lambda: handle_scan_entree("CONFIRM001", user), fg_color="#2A8C55", text_color="white")
    button_conf.pack(anchor="center")


mode_supp = False
emplacement = ""
produits_scannes = {}
user = ""

def get_produits_scannes_a():
    global produits_scannes
    return produits_scannes

def handle_scan_entree(produit_id, username):
    global mode_supp, emplacement, produits_scannes, user

    user = username
    produit_id = str(produit_id)

    try:
        if mode_supp:
            produit_info = get_produit_info(produit_id)
            if produit_id in produits_scannes:
                del produits_scannes[produit_id]
                for item in tree_ajouter.winfo_children():
                    if item.winfo_children()[0].cget("text") == produit_info["nom"]:
                        item.destroy()
                        break
                label_status.configure(text=f"Produit {produit_info['nom']} supprimé.", text_color="green")
                mode_supp = False
            else:
                label_status.configure(text=f"Produit {produit_info['nom']} non trouvé.", text_color="red")
            return

        if produit_id == "SUPP001":
            mode_supp = True
            label_status.configure(text="Mode suppression activé. Scannez un produit à supprimer.")
            return

        if produit_id == "CONFIRM001":
            if produits_scannes:

                message = f"Entrée stock :\n\n"

                for produit_id, infos in produits_scannes.items():
                    message += f"- {infos['nom']} : {infos['quantite_scannee']} unités\n"
                    add_record_ajouter_to_airtable_gestion(produit_id, infos["quantite_scannee"], username)
                envoie_msg_stock(message)
                produits_scannes.clear()

                for item in tree_ajouter.winfo_children():
                    # Par exemple, si les en-têtes ont une couleur différente
                    if item.cget("fg_color") != "#2A8C55":  # Couleur des en-têtes
                        item.destroy()

                label_status.configure(text=f"Tous les produits ont été ajoutés au stock.", text_color="green")
            else:
                label_status.configure(text="Aucun produit à confirmer.", text_color="red")
            return

        if produit_id not in ["RED001", "ACC001", "AJT001", "SCANPROD"]:
            produit_info = get_produit_info(produit_id)
            if produit_info:
                if produit_id in produits_scannes:
                    produits_scannes[produit_id]["quantite_scannee"] += 1
                    for row in tree_ajouter.winfo_children():
                        if row.winfo_children()[0].cget("text") == produit_info["nom"]:
                            row.winfo_children()[3].configure(text=produits_scannes[produit_id]["quantite_scannee"])
                            break
                    label_status.configure(text=f"Quantité scannée mise à jour pour {produit_info['nom']}.", text_color="green")
                else:
                    produits_scannes[produit_id] = {
                        "nom": produit_info["nom"],
                        "fournisseur": produit_info["fournisseur"],
                        "quantite_stock": produit_info["qte"],
                        "quantite_scannee": 1
                    }
                    row_frame = CTkFrame(tree_ajouter, fg_color="#f7f7f7")
                    row_frame.pack(fill="x", pady=0)
                    CTkLabel(row_frame, width=550, text=produit_info["nom"], font=("Arial", 18)).pack(side="left", anchor="center")
                    CTkLabel(row_frame, width=150, text=produit_info["fournisseur"], font=("Arial", 18)).pack(side="left", anchor="center")
                    CTkLabel(row_frame, width=80, text=produit_info["qte"], font=("Arial", 18)).pack(side="left", anchor="center", padx=50)
                    CTkLabel(row_frame, width=80, text=1, font=("Arial", 18)).pack(side="left", anchor="center", padx=75)
                    label_status.configure(text=f"Produit {produit_info['nom']} ajouté.")
            else:
                label_status.configure(text=f"Produit {produit_id} non trouvé.", text_color="red")
    except Exception as e:
        print(f"Erreur: {str(e)}")
        label_status.configure(text=f"Erreur: {str(e)}", text_color="red")
