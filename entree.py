from customtkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from tkinter.font import Font
from produits import get_produit_info, add_record_ajouter_to_airtable_gestion, envoie_msg_stock


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
    scrollable_frame = CTkScrollableFrame(tab_entree, width=1700, height=700, fg_color="white")
    scrollable_frame.pack(padx=15, pady=(0, 10))

    # Noms des colonnes
    columns = ["Nom", "Fournisseur", "Catégorie", "Quantité Stock", "Quantité Scannée"]

    # Définir une police pour mesurer les dimensions du texte
    header_font = Font(family="Arial", size=12, weight="bold")

    # Ajouter les en-têtes des colonnes avec un calcul dynamique de largeur
    header_frame = CTkFrame(scrollable_frame, fg_color="#2A8C55")
    header_frame.pack(fill="x", pady=0)

    # Largeurs des colonnes
    DEFAULT_COLUMN_WIDTH = 200
    SPECIFIC_COLUMN_WIDTH = 500

    column_widths = {
        "Nom": SPECIFIC_COLUMN_WIDTH,
        "Fournisseur": DEFAULT_COLUMN_WIDTH,
        "Catégorie": SPECIFIC_COLUMN_WIDTH,
        "Quantité Stock": DEFAULT_COLUMN_WIDTH,
        "Quantité Scannée": DEFAULT_COLUMN_WIDTH,
    }


    for col in columns:
        header_label = CTkLabel(
            header_frame,
            text=col,
            width=column_widths[col],
            font=("Arial", 18, "bold"),
            text_color="#fff",
            fg_color="#2A8C55",
            anchor="center"
        )
        header_label.pack(side="left")

    # Exemple de données pour le tableau (les informations produits)
    # Note: table_data = [] implies no data for now
    table_data = []

    row_font = Font(family="Arial", size=12)

    for row in table_data:
        row_frame = CTkFrame(scrollable_frame, fg_color="#f7f7f7")
        row_frame.pack(fill="x", pady=0)

        for i, item in enumerate(row):
            width = adjust_column_width(str(item), row_font, min_width=column_widths[i])
            entry = CTkEntry(
                row_frame,
                width=width,
                state="normal",
                justify="center",
                fg_color="#f7f7f7",
                font=("Arial", 18),
                border_width=0,
                text_color="#333",
            )
            entry.insert(0, item)
            entry.pack(side="left")

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

    label_status_societe = CTkLabel(
        tab_entree,
        text="Societe : ",
        font=("Arial", 26, "bold"),
        text_color="#2525fe",
        fg_color="#f7f7f7"
    )
    label_status_societe.pack(pady=(5, 15))

    texte_sous_tableau = CTkLabel(
        tab_entree,
        text="",
        font=("Arial", 12),
        text_color="#555",
        fg_color="#f7f7f7",
        wraplength=600,
        anchor="center"
    )
    texte_sous_tableau.pack(pady=10)


mode_supp = False
emplacement =""
societe = ""
produits_scannes = {}

def get_produits_scannes_a():
    global produits_scannes
    return produits_scannes

def handle_scan_entree(produit_id, username):
    global mode_supp, emplacement, produits_scannes, societe

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
                label_status.configure(text=f"Produit {produit_info['nom']} supprimé.")
                mode_supp = False
            else:
                label_status.configure(text=f"Produit {produit_info['nom']} non trouvé.")
            return

        if produit_id == "SUPP001":
            mode_supp = True
            label_status.configure(text="Mode suppression activé. Scannez un produit à supprimer.")
            return

        if produit_id == "CONFIRM001":
            if produits_scannes and societe:

                message = f"Entrée stock {societe} :\n\n"

                for produit_id, infos in produits_scannes.items():
                    message += f"- {infos['nom']} : {infos['quantite_scannee']} unités\n"
                    add_record_ajouter_to_airtable_gestion(produit_id, infos["quantite_scannee"], username, societe)
                envoie_msg_stock(message)
                produits_scannes.clear()

                for item in tree_ajouter.winfo_children():
                    # Par exemple, si les en-têtes ont une couleur différente
                    if item.cget("fg_color") != "#2A8C55":  # Couleur des en-têtes
                        item.destroy()

                label_status.configure(text=f"Tous les produits ont été ajouté au stock.")
            else:
                label_status.configure(text="Aucun produit à confirmer ou société manquant.")
            return

        if produit_id in ["ISE", "VF", "HSE"]:
            societe = produit_id
            label_status_societe.configure(text=f"Societe : {societe}")
            return

        if produit_id not in ["RED001", "ACC001", "AJT001"]:
            produit_info = get_produit_info(produit_id)
            if produit_info:
                if produit_id in produits_scannes:
                    produits_scannes[produit_id]["quantite_scannee"] += 1
                    for row in tree_ajouter.winfo_children():
                        if row.winfo_children()[0].cget("text") == produit_info["nom"]:
                            row.winfo_children()[4].configure(text=produits_scannes[produit_id]["quantite_scannee"])
                            break
                    label_status.configure(text=f"Quantité scannée mise à jour pour {produit_info['nom']}.")
                else:
                    produits_scannes[produit_id] = {
                        "nom": produit_info["nom"],
                        "fournisseur": produit_info["fournisseur"],
                        "categorie": produit_info["categorie"],
                        "quantite_stock": produit_info["qte"],
                        "quantite_scannee": 1
                    }
                    row_frame = CTkFrame(tree_ajouter, fg_color="#f7f7f7")
                    row_frame.pack(fill="x", pady=0)
                    CTkLabel(row_frame, width=500, text=produit_info["nom"], font=("Arial", 18)).pack(side="left", anchor="center")
                    CTkLabel(row_frame, width=200, text=produit_info["fournisseur"], font=("Arial", 18)).pack(side="left", anchor="center")
                    CTkLabel(row_frame, width=500, text=produit_info["categorie"], font=("Arial", 18)).pack(side="left", anchor="center")
                    CTkLabel(row_frame, width=200, text=str(produit_info["qte"]), font=("Arial", 18)).pack(side="left", anchor="center")
                    CTkLabel(row_frame, width=200, text=1, font=("Arial", 18)).pack(side="left", anchor="center")
                    label_status.configure(text=f"Produit {produit_info['nom']} ajouté.")
            else:
                label_status.configure(text=f"Produit {produit_id} non trouvé.", text_color="red")
    except Exception as e:
        print(f"Erreur: {str(e)}")
        label_status.configure(text=f"Erreur: {str(e)}", text_color="red")