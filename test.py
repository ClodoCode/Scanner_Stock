from tkinter import *
from customtkinter import *
from functools import partial
from fonction import get_produit_info, add_record_ajouter_to_airtable_gestion, envoie_msg_stock

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

# Dictionnaires pour suivre les produits scannés et leurs images
produits_scannes = {}

mode_supp = False
emplacement = ""
societe = None  # Exemple de variable qui pourrait être utilisée pour le check de société

def get_produits_scannes_t():
    global produits_scannes
    return produits_scannes

def handle_scan_entree_test(produit_id, username):
    global mode_supp, emplacement, produits_scannes, societe

    produit_id = str(produit_id)

    try:
        # Mode suppression activé
        if mode_supp:
            produit_info = get_produit_info(produit_id)
            if produit_id in produits_scannes:
                del produits_scannes[produit_id]
                update_product_table(get_produits_scannes_t().values(), table_frame, username)
                #label_status.configure(text=f"Produit {produit_info['nom']} supprimé.")
                mode_supp = False
            else:
                label_status.configure(text=f"Produit {produit_info['nom']} non trouvé.")
            return

        # Passer en mode suppression
        if produit_id == "SUPP001":
            mode_supp = True
            #label_status.configure(text="Mode suppression activé. Scannez un produit à supprimer.")
            return

        # Confirmer l'entrée en stock
        if produit_id == "CONFIRM001":
            if produits_scannes and societe:
                message = f"Entrée stock :\n\n"
                for produit_id, infos in produits_scannes.items():
                    message += f"- {infos['nom']} : {infos['quantite_scannee']} unités\n"
                    add_record_ajouter_to_airtable_gestion(produit_id, infos["quantite_scannee"], username)
                envoie_msg_stock(message)
                produits_scannes.clear()
                update_product_table(get_produits_scannes_t().values(), table_frame, username)  # Mettre à jour l'affichage
                #label_status.configure(text=f"Tous les produits ont été ajoutés au stock.")
            #else:
                #label_status.configure(text="Aucun produit à confirmer ou société manquant.", text_color="red")
            return

        # Si ce n'est pas un code spécial, scanne un produit
        if produit_id not in ["RED001", "ACC001", "AJT001", "SCANPROD"]:
            produit_info = get_produit_info(produit_id)
            if produit_info:
                if produit_id in produits_scannes:
                    produits_scannes[produit_id]["quantite_scannee"] += 1
                    update_product_table(get_produits_scannes_t().values(), table_frame, username)  # Mise à jour après scan
                   # label_status.configure(text=f"Quantité scannée mise à jour pour {produit_info['nom']}.")
                else:
                    produits_scannes[produit_id] = {
                        "nom": produit_info["nom"],
                        "fournisseur": produit_info["fournisseur"],
                        "quantite_stock": produit_info["qte"],
                        "quantite_scannee": 1
                    }
                    update_product_table(get_produits_scannes_t().values(), table_frame, username)  # Mise à jour après ajout
                   # label_status.configure(text=f"Produit {produit_info['nom']} ajouté.")
           # else:
                #label_status.configure(text=f"Produit {produit_id} non trouvé.", text_color="red")
    except Exception as e:
        print(f"Erreur: {str(e)}")
        #label_status.configure(text=f"Erreur: {str(e)}", text_color="red")

def show_all_products(main_view, username):
    global table_frame, username_la

    username_la = username

    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    # Bloc pour afficher les produits scannés avec scrollable frame
    scrollable_frame = CTkScrollableFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Ajouter un texte explicatif au-dessus du tableau
    description_label = CTkLabel(
        scrollable_frame,
        text="Liste des produits scannés et la quantité en stock.",
        font=("Arial", 18),
        text_color=TEXT_COLOR,
        anchor="w",
        width=500,
        height=40
    )
    description_label.pack(pady=(0, 10))

    # Tableau des produits
    table_frame = CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Créer les en-têtes
    create_table_headers(table_frame)

    # Ajouter les produits scannés dans la liste
    update_product_table(produits_scannes.values(), table_frame, username_la)

def create_table_headers(table_frame):
    """Crée les en-têtes de colonnes pour la table des produits avec un bandeau gris clair."""
    headers = ["Nom", "Fournisseur", "Quantité en Stock", "Quantité Scannée"]

    # Ajouter un bandeau gris clair sous les en-têtes
    header_bg_label = CTkLabel(
        table_frame,
        text=" " * 100,  # L'important est de faire un label large
        fg_color="#d3d3d3",  # Fond gris clair
        width=10000,  # Largeur importante pour couvrir toute la zone
        height=30  # Hauteur de la ligne d'en-tête
    )
    header_bg_label.grid(row=0, column=0, columnspan=len(headers), sticky="nsew")

    # Créer les en-têtes de colonnes
    for col, header in enumerate(headers):
        table_frame.grid_columnconfigure(col, weight=1)  # Colonnes extensibles

        # Ajouter les cadres d'en-tête
        header_frame = CTkFrame(
            table_frame,
            fg_color="transparent",  # Transparent pour laisser voir le fond gris clair
            corner_radius=8
        )
        header_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        header_frame.tag = "header"

        # Ajouter une étiquette pour chaque colonne
        header_label = CTkLabel(
            header_frame,
            text=header,
            font=("Arial Bold", 20),
            text_color="#333333"
        )
        header_label.pack(padx=10, pady=10)

def update_product_table(products, table_frame, username):
    """Met à jour uniquement les lignes des produits dans la table."""
    for widget in table_frame.winfo_children():
        if getattr(widget, "tag", None) != "header":
            widget.destroy()

    for row, product in enumerate(products, start=1):
        # Définir la couleur du texte par défaut
        text_color = TEXT_COLOR

        # Créer les labels et les ajouter à la table
        name_label = CTkLabel(
            table_frame, text=product["nom"], font=("Arial", 16), text_color=text_color
        )
        name_label.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")

        fournisseur_label = CTkLabel(
            table_frame, text=product["fournisseur"], font=("Arial", 16), text_color=text_color
        )
        fournisseur_label.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")

        # Afficher la quantité en stock
        stock_label = CTkLabel(
            table_frame, text=str(product["quantite_stock"]), font=("Arial", 16), text_color=text_color
        )
        stock_label.grid(row=row, column=2, padx=5, pady=5, sticky="nsew")

        # Afficher la quantité scannée
        quantity_label = CTkLabel(
            table_frame, text=str(product["quantite_scannee"]), font=("Arial", 16), text_color=text_color
        )
        quantity_label.grid(row=row, column=3, padx=5, pady=5, sticky="nsew")

        # Ajouter les labels au dictionnaire `product`
        product["name_label"] = name_label
        product["quantity_label"] = quantity_label
        product["fournisseur_label"] = fournisseur_label
        product["stock_label"] = stock_label
