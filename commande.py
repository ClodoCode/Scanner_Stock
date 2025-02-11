from tkinter import *
from CTkTable import *
import threading
import time
from queue import Queue
import customtkinter as ctk
from customtkinter import *
from functools import partial
from fonction import list_command, get_produit_info, confirm_command, add_recption_cde

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"


def show_commande(main_view):
    """Affiche les commandes et permet de filtrer entre complètes et incomplètes sans rechargement."""

    print("⏳ Chargement des commandes...")

    # Supprimer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()

    # --- Conteneur principal ---
    content_frame = CTkFrame(main_view, fg_color="transparent")
    content_frame.pack(expand=True, fill="both")

    # --- Boutons de sélection ---
    button_frame = CTkFrame(content_frame, fg_color=BG_COLOR, corner_radius=15)
    button_frame.pack(fill="x", padx=20, pady=10)

    info_frame = CTkFrame(content_frame, fg_color="transparent")  # Cadre pour afficher les infos
    commandes_frame = CTkFrame(content_frame, fg_color="transparent")

    info_frame.pack(fill="x", padx=20, pady=10)  # On met les infos au-dessus
    commandes_frame.pack(expand=True, fill="both", padx=20, pady=10)

    # --- Stockage des commandes en mémoire ---
    commandes_info = []

    def load_data(force_reload=False):
        """Charge les commandes UNE SEULE FOIS au premier affichage, sauf si actualisation."""
        print(f"⏳ Chargement des commandes en mémoire...")

        # Supprimer les commandes existantes uniquement si c'est une actualisation
        if force_reload:
            for widget in commandes_frame.winfo_children():
                widget.destroy()
            for widget in info_frame.winfo_children():
                widget.destroy()

        # Affichage du chargement
        loading_label = CTkLabel(commandes_frame, text="Chargement...", font=("Arial", 18), text_color="gray")
        loading_label.pack(pady=10)

        def fetch_data():
            nonlocal commandes_info
            try:
                commandes = list_command()
                commandes_info = recup_commandes_info(commandes)
            except Exception as e:
                commandes_info = []
                print(f"❌ Erreur lors du chargement des commandes: {e}")

            main_view.after(100, lambda: display_filtered_commandes("incomplètes"))

        threading.Thread(target=fetch_data, daemon=True).start()

    def display_filtered_commandes(command_type):
        """Affiche les commandes sélectionnées sans les recharger de la base de données."""
        print(f"🔍 Filtrage des commandes {command_type}...")

        # Supprimer les commandes existantes
        for widget in commandes_frame.winfo_children():
            widget.destroy()
        for widget in info_frame.winfo_children():
            widget.destroy()

        # Filtrage local des commandes déjà chargées
        filtered_commandes = [c for c in commandes_info if (c["status"] == "Complète") == (command_type == "complètes")]

        if not filtered_commandes:
            CTkLabel(commandes_frame, text="Aucune commande trouvée.", font=("Arial", 18), text_color="red").pack(pady=20)
            return

        # --- Affichage des infos seulement pour commandes incomplètes ---
        if command_type == "incomplètes":
            info_data = [
                ("Total Commandes Incomplètes", len(filtered_commandes)),
                ("Fournisseurs Uniques", len(set(c["fournisseur"] for c in filtered_commandes))),
                ("Produits Totaux", sum(len(c.get("produits", [])) for c in filtered_commandes))
            ]

            info_frame.configure(fg_color=BG_COLOR)  # Appliquer la couleur de fond
            for label, value in info_data:
                block = CTkFrame(info_frame, fg_color="white", corner_radius=10, width=120, height=80)
                block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
                CTkLabel(block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR).pack(pady=5)
                CTkLabel(block, text=label, font=("Arial", 14), text_color=TEXT_COLOR).pack()
        else:
            # 🔥 Supprimer complètement le cadre des infos lorsqu'on affiche les commandes complètes
            for widget in info_frame.winfo_children():
                widget.destroy()
            info_frame.pack_forget()

        table_frame = CTkFrame(commandes_frame, fg_color="white", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        update_command_table(filtered_commandes, table_frame, is_complete=(command_type == "complètes"))

    # --- Création des boutons avec la nouvelle organisation ---
    CTkButton(button_frame, text="🚨 Commandes Incomplètes", command=lambda: display_filtered_commandes("incomplètes")).pack(side="left", padx=10, pady=5, expand=True)
    CTkButton(button_frame, text="🔄 Actualiser", command=lambda: load_data(force_reload=True)).pack(side="left", padx=10, pady=5, expand=True)
    CTkButton(button_frame, text="📦 Commandes Complètes", command=lambda: display_filtered_commandes("complètes")).pack(side="right", padx=10, pady=5, expand=True)

    # Charger les commandes UNE SEULE FOIS
    load_data()





def display_filtered_commandes(parent_frame, data_queue, loading_label):
    """Affiche uniquement les commandes sélectionnées après le filtrage."""
    commandes_info = data_queue.get()
    loading_label.destroy()

    if not commandes_info:
        CTkLabel(parent_frame, text="Aucune commande trouvée.", font=("Arial", 18), text_color="red").pack(pady=20)
        return

    table_frame = CTkFrame(parent_frame, fg_color="white", corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)

    update_command_table(commandes_info, table_frame, is_complete=(commandes_info[0]["status"] == "Complète"))



def display_commandes(main_view, data_queue, loading_frame):
    commandes_info = data_queue.get()
    loading_frame.destroy()

    if not commandes_info:
        CTkLabel(main_view, text="Aucune commande trouvée.", font=("Arial", 18), text_color="red").place(relx=0.5, rely=0.5, anchor="center")
        return

    content_frame = CTkFrame(main_view, fg_color="transparent")
    content_frame.pack(expand=True, fill="both")

    # Infos générales
    commandes_completes = [c for c in commandes_info if c["status"] == "Complète"]
    commandes_incompletes = [c for c in commandes_info if c["status"] == "Incomplète"]

    info_frame = CTkFrame(content_frame, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    info_labels = [
        ("Total Commandes", len(commandes_info)),
        ("Fournisseurs uniques", len(set(c["fournisseur"] for c in commandes_info))),
        ("Produits totaux", sum(len(c.get("produits", [])) for c in commandes_info)),
        ("Commandes Incomplètes", len(commandes_incompletes))
    ]

    for label, value in info_labels:
        block = CTkFrame(info_frame, fg_color="white", corner_radius=10, width=120, height=80)
        block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        CTkLabel(block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR).pack(pady=5)
        CTkLabel(block, text=label, font=("Arial", 14), text_color=TEXT_COLOR).pack()

    scrollable_frame = CTkFrame(content_frame, fg_color=BG_COLOR, corner_radius=15)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    if commandes_incompletes:
        create_section(scrollable_frame, "📌 Commandes Incomplètes", commandes_incompletes)

    if commandes_completes:
        create_section(scrollable_frame, "✅ Commandes Complètes", commandes_completes)


def create_section(parent, title, commandes):
    """Crée une section avec barre de défilement et en-têtes dynamiques."""
    section_frame = CTkFrame(parent, fg_color="white", corner_radius=15)
    section_frame.pack(fill="both", padx=10, pady=5, expand=True)

    section_label = CTkLabel(section_frame, text=title, font=("Arial Bold", 18), text_color="black")
    section_label.pack(pady=10)

    # Cadre avec barre de défilement
    table_scroll_frame = CTkFrame(section_frame, fg_color="white", height=300)
    table_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

    table_frame = CTkFrame(table_scroll_frame, fg_color="white", corner_radius=15)
    table_frame.pack(fill="both", expand=True)

    update_command_table(commandes, table_frame)


def update_command_table(commandes, parent_frame, is_complete=False):
    """Affichage optimisé des commandes avec en-têtes fixes et alignement parfait."""

    # Supprimer le contenu existant
    for widget in parent_frame.winfo_children():
        widget.destroy()

    headers = ["Produits", "Fournisseur", "Commandé", "Reçus", "Statut"]
    if not is_complete:
        headers.append("Actions")  # Ajout de la colonne Actions pour les commandes incomplètes

    # --- Cadre principal du tableau ---
    table_container = CTkFrame(parent_frame, fg_color="white")
    table_container.pack(fill="both", expand=True, padx=10, pady=5)

    # --- Création du cadre fixe pour les en-têtes ---
    header_frame = CTkFrame(table_container, fg_color=HEADER_BG, corner_radius=10)
    header_frame.pack(fill="x")

    # ✅ Assurer une largeur uniforme pour toutes les colonnes
    for col in range(len(headers)):
        header_frame.grid_columnconfigure(col, weight=1, uniform="header")

    for col, header in enumerate(headers):
        label = CTkLabel(header_frame, text=header, font=("Arial Bold", 16), text_color="white", anchor="center")
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    # --- Cadre pour les données ---
    table_frame = CTkFrame(table_container, fg_color="white")
    table_frame.pack(fill="both", expand=True)

    # ✅ Uniformiser la structure des colonnes
    for col in range(len(headers)):
        table_frame.grid_columnconfigure(col, weight=1, uniform="row")

    # --- Ajout des lignes des commandes ---
    for row, commande in enumerate(commandes, start=1):
        produits_noms = ", ".join([p.get("nom", "Produit inconnu") for p in commande.get("produits", [])])

        CTkLabel(table_frame, text=produits_noms, font=("Arial", 14), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
        CTkLabel(table_frame, text=commande["fournisseur"], font=("Arial", 14), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        CTkLabel(table_frame, text=str(commande["qte_cde"]), font=("Arial", 14), text_color=TEXT_COLOR, anchor="center").grid(row=row, column=2, padx=5, pady=5, sticky="nsew")

        qte_recu_label = CTkLabel(table_frame, text=str(commande["qte_recu"]), font=("Arial", 14), text_color=TEXT_COLOR, anchor="center")
        qte_recu_label.grid(row=row, column=3, padx=5, pady=5, sticky="nsew")

        status_label = CTkLabel(table_frame, text=commande["status"], font=("Arial", 14), text_color=TEXT_COLOR, anchor="center")
        status_label.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")

        # Bouton "Réceptionner" seulement pour les commandes incomplètes
        if not is_complete:
            action_frame = CTkFrame(table_frame, fg_color="transparent")
            action_frame.grid(row=row, column=5, padx=5, pady=5, sticky="nsew")

            CTkButton(
                action_frame,
                text="Réceptionner",
                command=partial(button_reception, commande["id"], commande["produits"][0]["id"], commande["qte_cde"], qte_recu_label, status_label),
            ).pack()



def recup_commandes_info(commandes):
    """Récupère et structure les données des commandes."""
    commandes_info = []
    for command in commandes:
        fournisseur = command.get("fournisseur", ["Inconnu"])
        fournisseur = fournisseur[0] if isinstance(fournisseur, list) and fournisseur else "Inconnu"

        produits = [get_produit_info(produit_id) or {"nom": "Produit inconnu"} for produit_id in command.get("Produits", [])]
        
        commandes_info.append({
            "num_cde": command.get("Num cde", "NC"),
            "fournisseur": fournisseur,
            "produits": produits,
            "status": command.get("status", "Non défini"),
            "qte_cde": command.get("qte_command", "0"),
            "qte_recu": command.get("qte_recu", "0"),
            "id": command.get("id", "Pas d'ID")
        })

    commandes_info.sort(key=lambda c: c["produits"][0].get("nom", "ZZZZZ").lower())
    return commandes_info


def button_reception(command_id, produit_id, qte_reception, qte_recu_label, status_label):
    def reception_task():
        if confirm_command(command_id, qte_reception):
            add_recption_cde(produit_id, qte_reception)
            time.sleep(0.5)

            qte_recu_nouveau = int(qte_recu_label.cget("text")) + qte_reception
            qte_recu_label.configure(text=str(qte_recu_nouveau))

            if qte_recu_nouveau >= int(qte_reception):
                status_label.configure(text="Complète")

    threading.Thread(target=reception_task).start()
