from tkinter import *
from CTkTable import *
import customtkinter as ctk
from customtkinter import *
from functools import partial  # Pour utiliser partial
from fonction import list_command, get_produit_info

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"


def show_commande(main_view):
    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    # Appeler la fonction list_command() pour récupérer les commandes
    commandes = list_command()

    # Récupérer les informations des commandes et des produits associés
    commandes_info = recup_commandes_info(commandes)

    # Afficher les informations générales sur les commandes (statistiques)
    info_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    info_labels = [
        ("Commandes en cours", len(commandes)),
        ("Fournisseurs uniques", len(set(c["Fournisseur"] for c in commandes))),
        ("Produits totaux", sum(len(c["Produits"]) for c in commandes)),
        ("Commandes en attente", sum(1 for c in commandes if c["status"] == "en attente"))
    ]

    for i, (label, value) in enumerate(info_labels):
        info_block = CTkFrame(info_frame, fg_color="#FFFFFF", corner_radius=10, width=120, height=80)
        info_block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        CTkLabel(info_block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR).pack(pady=5)
        CTkLabel(info_block, text=label, font=("Arial", 20), text_color=TEXT_COLOR).pack()

    # Bloc pour afficher les commandes avec scrollbar
    scrollable_frame = CTkScrollableFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Tableau des commandes
    table_frame = CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Créer les en-têtes
    create_table_headers(table_frame)

    # Ajouter les commandes dans la liste
    update_command_table(commandes, table_frame)


def recup_commandes_info(commandes):
    """Récupère les informations sur les produits dans les commandes."""
    commandes_info = []
    for command in commandes:
        print(f"Commande : {command}")  # Afficher la commande pour vérifier sa structure
        if "Fournisseur" in command:
            command_info = {
                "id": command["id"],
                "fournisseur": command.get("Fournisseur", "Inconnu"),  # C'est ici qu'on accède à "Fournisseur"
                "produits": [get_produit_info(produit_id) for produit_id in command.get('Produits', [])],
                "status": command.get("status", "Non défini")
            }
            commandes_info.append(command_info)
        else:
            print(f"Commande sans 'Fournisseur' : {command}")  # Afficher les commandes sans la clé 'Fournisseur'
    return commandes_info



def create_table_headers(table_frame):
    """Crée les en-têtes de colonnes pour le tableau des commandes."""
    headers = ["ID Commande", "Fournisseur", "Produits", "Statut", "Actions"]

    # Ajouter un bandeau gris clair sous les en-têtes
    header_bg_label = CTkLabel(
        table_frame,
        text=" " * 100,
        fg_color="#d3d3d3",  
        width=10000,
        height=30
    )
    header_bg_label.grid(row=0, column=0, columnspan=len(headers), sticky="nsew")

    # Créer les colonnes et les en-têtes
    for col, header in enumerate(headers):
        table_frame.grid_columnconfigure(col, weight=1)  # Colonnes extensibles
        header_frame = CTkFrame(table_frame, fg_color="transparent", corner_radius=8)
        header_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        header_label = CTkLabel(
            header_frame,
            text=header,
            font=("Arial Bold", 20),
            text_color="#333333"
        )
        header_label.pack(padx=10, pady=10)


def update_command_table(commandes, table_frame):
    """Met à jour la table avec les informations des commandes."""
    for widget in table_frame.winfo_children():
        if getattr(widget, "tag", None) != "header":
            widget.destroy()

    for row, commande in enumerate(commandes, start=1):
        CTkLabel(
            table_frame, text=commande["id"], font=("Arial", 16), text_color=TEXT_COLOR
        ).grid(row=row, column=0, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            table_frame, text=commande["fournisseur"], font=("Arial", 16), text_color=TEXT_COLOR
        ).grid(row=row, column=1, padx=5, pady=5, sticky="nsew")

        # Affichage des produits dans la commande
        produits_noms = ", ".join([p["nom"] for p in commande["produits"]])
        CTkLabel(
            table_frame, text=produits_noms, font=("Arial", 16), text_color=TEXT_COLOR
        ).grid(row=row, column=2, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            table_frame, text=commande["status"], font=("Arial", 16), text_color=TEXT_COLOR
        ).grid(row=row, column=3, padx=5, pady=5, sticky="nsew")

        # Ajout des actions pour chaque commande
        action_frame = CTkFrame(table_frame, fg_color="transparent")
        action_frame.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")
        CTkButton(
            action_frame, text="Marquer comme Livré", width=150, command=partial(update_status, commande["id"])
        ).pack(side="left", padx=5)


def update_status(command_id):
    """Met à jour le statut de la commande (par exemple, marquer comme livrée)."""
    print(f"Commande {command_id} marquée comme livrée.")
    # Code pour mettre à jour le statut dans la base de données


