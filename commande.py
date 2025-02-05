from tkinter import *
from CTkTable import *
import threading
import time
import customtkinter as ctk
from customtkinter import *
from functools import partial
from fonction import list_command, get_produit_info, confirm_command

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

def show_commande(main_view):
    global table_frame

    print("⏳ Chargement des commandes...")

    # Supprimer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()

    # Cadre central pour la barre de chargement (sans pack, pour éviter le décalage)
    loading_frame = CTkFrame(main_view, fg_color="transparent")

    # Centrage absolu du cadre
    loading_frame.place(relx=0.5, rely=0.5, anchor="center")

    loading_label = CTkLabel(loading_frame, text="Chargement...", font=("Arial", 18), text_color="gray")
    loading_label.pack(pady=10)

    loading_bar = CTkProgressBar(loading_frame, mode="indeterminate", width=200, height=10)
    loading_bar.pack(pady=10)
    loading_bar.start()

    def load_data():
        start_time = time.time()

        commandes = list_command()
        commandes_info = recup_commandes_info(commandes)

        end_time = time.time()
        print(f"✅ Commandes chargées en {end_time - start_time:.2f} secondes.")

        # Mise à jour de l'UI après chargement
        main_view.after(0, lambda: display_commandes(main_view, commandes_info, loading_frame))

    # Charger les commandes en arrière-plan
    thread = threading.Thread(target=load_data)
    thread.start()


def display_commandes(main_view, commandes_info, loading_frame):
    # Supprimer la barre de chargement après le chargement
    loading_frame.destroy()

    # Cadre principal pour l'affichage final (s'assure que le tableau remplit bien l'espace)
    content_frame = CTkFrame(main_view, fg_color="transparent")
    content_frame.pack(expand=True, fill="both")

    info_frame = CTkFrame(content_frame, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    if not commandes_info:
        print("⚠️ Aucune commande trouvée.")
        return

    # Infos générales
    info_labels = [
        ("Commandes en cours", len(commandes_info)),
        ("Fournisseurs uniques", len(set(c["fournisseur"] for c in commandes_info))),
        ("Produits totaux", sum(len(c.get("produits", [])) for c in commandes_info)),
        ("Commandes en attente", sum(1 for c in commandes_info if c.get("status", "") == "Incomplète"))
    ]

    for label, value in info_labels:
        info_block = CTkFrame(info_frame, fg_color="#FFFFFF", corner_radius=10, width=120, height=80)
        info_block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        CTkLabel(info_block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR).pack(pady=5)
        CTkLabel(info_block, text=label, font=("Arial", 20), text_color=TEXT_COLOR).pack()

    # Zone de défilement pour le tableau
    scrollable_frame = CTkScrollableFrame(content_frame, fg_color=BG_COLOR, corner_radius=15)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Cadre pour les en-têtes
    header_frame = CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
    header_frame.pack(fill="x", padx=10, pady=5)
    create_table_headers(header_frame)

    # Cadre pour le contenu du tableau
    table_frame = CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    update_command_table(commandes_info, table_frame, main_view)




def create_table_headers(header_frame):
    headers = ["ID Commande", "Fournisseur", "Produits", "Commandé", "Reçus", "Statut", "Actions"]

    # Configuration des colonnes pour éviter le décalage
    for col in range(len(headers)):
        header_frame.grid_columnconfigure(col, weight=1, uniform="header")

    # Création des en-têtes alignées
    for col, header in enumerate(headers):
        header_label = CTkLabel(
            header_frame,
            text=header,
            font=("Arial Bold", 14),
            text_color="black",
            fg_color="transparent",
            width=150,  # Forcer une largeur uniforme
            height=30
        )
        header_label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    print("En-têtes créés et bien alignés.")




def update_command_table(commandes, table_frame, main_view):
    # Supprimer uniquement les anciennes lignes sans toucher aux en-têtes
    for widget in table_frame.winfo_children():
        widget.destroy()

    if not commandes:
        print("⚠️ Aucune commande à afficher.")
        return

    # Configuration des colonnes pour assurer un bon alignement
    for col in range(7):  # 7 colonnes en tout
        table_frame.grid_columnconfigure(col, weight=1, uniform="table")

    for row, commande in enumerate(commandes, start=1):

        CTkLabel(table_frame, text=commande["num_cde"], font=("Arial", 16), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        CTkLabel(table_frame, text=commande["fournisseur"], font=("Arial", 16), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=1, padx=5, pady=5, sticky="ew")

        produits_noms = ", ".join([p.get("nom", "Produit inconnu") for p in commande.get("produits", [])])
        CTkLabel(table_frame, text=produits_noms, font=("Arial", 16), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=2, padx=5, pady=5, sticky="ew")

        CTkLabel(table_frame, text=commande["qte_cde"], font=("Arial", 16), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=3, padx=5, pady=5, sticky="ew")

        # Label mis à jour dynamiquement pour la quantité reçue
        qte_recu_label = CTkLabel(table_frame, text=str(commande["qte_recu"]), font=("Arial", 16), text_color=TEXT_COLOR, anchor="center")
        qte_recu_label.grid(row=row, column=4, padx=5, pady=5, sticky="ew")

        CTkLabel(table_frame, text=commande["status"], font=("Arial", 16), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=5, padx=5, pady=5, sticky="ew")

        qte_cde = int(commande.get("qte_cde", 0))
        qte_recu = int(commande.get("qte_recu", 0))
        qte_reception = qte_cde - qte_recu

        # Bouton "Réceptionner"
        action_frame = CTkFrame(table_frame, fg_color="transparent")
        action_frame.grid(row=row, column=6, padx=5, pady=5, sticky="nsew")

        status_label = CTkLabel(table_frame, text=commande["status"], font=("Arial", 16), text_color=TEXT_COLOR)
        status_label.grid(row=row, column=5, padx=5, pady=5, sticky="ew")

        # Bouton "Réceptionner" avec passage de `status_label`
        CTkButton(
            action_frame, 
            text="Réceptionner", 
            width=100,  
            command=partial(button_reception, commande["id"], qte_reception, qte_recu_label, status_label)
        ).pack(anchor="center", padx=5)


def recup_commandes_info(commandes):
    commandes_info = []
    for command in commandes:
        print(f"Traitement de la commande: {command}")  # Debugging

        if "Num cde" in command and "fournisseur" in command:  # Correction ici
            fournisseur = command["fournisseur"]
            if isinstance(fournisseur, list):  # Vérifier si c'est une liste
                fournisseur = fournisseur[0] if fournisseur else "Inconnu"

            command_info = {
                "num_cde": command["Num cde"],
                "fournisseur": fournisseur,  
                "produits": [get_produit_info(produit_id) or {"nom": "Produit inconnu"} for produit_id in command.get("Produits", [])],
                "status": command.get("status", "Non défini"),
                "qte_cde": command.get("qte_command", "Pas de qte commandé"),
                "qte_recu": command.get("qte_recu", "Pas de qte reçus"),
                "id": command.get("id", "Pas d'ID")  # Correction ici
            }
            commandes_info.append(command_info)

    return commandes_info

def button_reception(command_id, qte_reception, qte_recu_label, status_label):
    def reception_task():
        if confirm_command(command_id, qte_reception):
            print(f"✅ Commande {command_id} mise à jour avec {qte_reception} reçus.")

            # Attendre pour s'assurer que la base de données a bien été mise à jour
            time.sleep(0.5)

            # Mettre à jour directement les labels sans retraiter toutes les commandes
            qte_recu_actuel = int(qte_recu_label.cget("text"))  # Récupère la valeur actuelle
            qte_recu_nouveau = qte_recu_actuel + qte_reception  # Ajoute la réception

            # Mettre à jour dynamiquement l'affichage
            qte_recu_label.configure(text=str(qte_recu_nouveau))

            # Si la quantité reçue atteint la quantité commandée, on met le statut à "Complète"
            if qte_recu_nouveau >= int(qte_recu_label.master.grid_slaves(row=qte_recu_label.grid_info()["row"], column=3)[0].cget("text")):
                print(f"✅ Commande {command_id} maintenant Complète.")
                status_label.configure(text="Complète")

    # Exécuter la mise à jour en arrière-plan pour éviter de bloquer l'interface
    thread = threading.Thread(target=reception_task)
    thread.start()