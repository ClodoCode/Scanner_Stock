from customtkinter import *
import tkinter
import time
import threading
from tkinter.font import Font
from fonction import cree_prod, get_produit_info, crea_command

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

produits_scannes = {}
scan_ok = ""
user = ""
mode_supp = False

def show_creer(main_view):
    """Affiche l'interface de création de produit."""
    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    global fields_frame, produit_frame, scan_ok, label_status

    scan_ok = "pas ok"
    print(f"{scan_ok}")

    # Conteneur principal
    main_view.configure(bg_color=BG_COLOR)
    
    # Titre
    button_frame = CTkFrame(main_view, fg_color="transparent", corner_radius=15)
    button_frame.pack(fill="x", padx=20, pady=5)

    button_produit = CTkButton(button_frame, text="Produit", command=lambda : crea_prod(main_view))
    button_produit.pack(side="left", padx=10, pady=10)

    button_commande = CTkButton(button_frame, text="Commande", command=lambda : command(main_view))
    button_commande.pack(side="left", padx=10, pady=10)

    # Conteneur des champs
    fields_frame = CTkFrame(master=main_view, fg_color="#4b5e61", corner_radius=15)
    fields_frame.pack(fill="both", padx=27, pady=20)

    label_status = CTkLabel(
        main_view,
        text="",
        font=("Arial", 18, "italic"),
        text_color="green",
        fg_color="transparent"
    )
    label_status.pack(pady=(5, 15))

    crea_prod(main_view)

def crea_prod(main_view):
    global scan_ok
    for widget in fields_frame.winfo_children():
        widget.destroy()

    scan_ok = "pas ok"

    # Configuration du frame principal
    fields_frame.columnconfigure(0, weight=1)
    fields_frame.columnconfigure(1, weight=1)

    # Titre
    title_label = CTkLabel(fields_frame, text="Création de Produit", font=("Arial Black", 25), text_color="white")
    title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20, sticky="ew")

    # Fonction pour créer un champ avec un label
    def create_entry_field(label_text, row):
        label = CTkLabel(fields_frame, text=label_text, font=("Arial Bold", 17), text_color="white")
        label.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 0))

        entry = CTkEntry(fields_frame, fg_color="white", text_color="black", corner_radius=8)
        entry.grid(row=row + 1, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 10))
        return entry

    # Champs d'entrée
    nom_entry = create_entry_field("Nom du Produit", 1)
    ref_entry = create_entry_field("Référence Produit", 3)

    # Menus déroulants
    categories = ["BUSE", "CALE", "CHEVILLE", "CLIENT", "COFFRET", "CONSOMMABLE", "DISQUE", "ELECTRICITE", "EMBOUT"]
    fournisseurs = ["SOMFY", "AMAZON", "MANO MANO", "FOUSSIER", "WURTH"]

    category_label = CTkLabel(fields_frame, text="Catégorie", font=("Arial Bold", 17), text_color="white")
    category_label.grid(row=5, column=0, sticky="w", padx=20, pady=(10, 0))

    category_menu = CTkOptionMenu(fields_frame, values=categories, fg_color="white", text_color="black", corner_radius=8)
    category_menu.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 10))

    supplier_label = CTkLabel(fields_frame, text="Fournisseur", font=("Arial Bold", 17), text_color="white")
    supplier_label.grid(row=7, column=0, sticky="w", padx=20, pady=(10, 0))

    supplier_menu = CTkOptionMenu(fields_frame, values=fournisseurs, fg_color="white", text_color="black", corner_radius=8)
    supplier_menu.grid(row=8, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 10))

    # Quantité avec boutons + et -
    quantity_label = CTkLabel(fields_frame, text="Quantité", font=("Arial Bold", 17), text_color="white")
    quantity_label.grid(row=9, column=0, sticky="w", padx=20, pady=(10, 0))

    quantity_frame = CTkFrame(fields_frame, fg_color="transparent")
    quantity_frame.grid(row=10, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 10))

    quantity_var = tkinter.IntVar(value=1)
    
    def increase_quantity():
        quantity_var.set(quantity_var.get() + 1)

    def decrease_quantity():
        if quantity_var.get() > 0:
            quantity_var.set(quantity_var.get() - 1)

    minus_button = CTkButton(quantity_frame, text="-", width=30, command=decrease_quantity)
    minus_button.pack(side="left", padx=(0, 10))

    quantity_display = CTkLabel(quantity_frame, textvariable=quantity_var, font=("Arial Bold", 16), text_color="white")
    quantity_display.pack(side="left", padx=(0, 10))

    plus_button = CTkButton(quantity_frame, text="+", width=30, command=increase_quantity)
    plus_button.pack(side="left")

    # Champs pour le prix
    price_entry = create_entry_field("Prix", 11)

    # Champs Min/Max
    min_max_frame = CTkFrame(fields_frame, fg_color="transparent")
    min_max_frame.grid(row=13, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 10))

    min_label = CTkLabel(min_max_frame, text="Minimum", font=("Arial Bold", 17), text_color="white")
    min_label.pack(anchor="w", pady=(10, 0))

    min_entry = CTkEntry(min_max_frame, fg_color="white", text_color="black", corner_radius=8)
    min_entry.pack(fill="x", pady=(5, 10))

    max_label = CTkLabel(min_max_frame, text="Maximum", font=("Arial Bold", 17), text_color="white")
    max_label.pack(anchor="w", pady=(10, 0))

    max_entry = CTkEntry(min_max_frame, fg_color="white", text_color="black", corner_radius=8)
    max_entry.pack(fill="x", pady=(5, 10))

    # Bouton "Créer"
    def handle_create():
        nom = nom_entry.get()
        ref = ref_entry.get()
        categorie = category_menu.get()
        fournisseur = supplier_menu.get()
        quantite = quantity_var.get()
        prix = price_entry.get()
        min_val = min_entry.get()
        max_val = max_entry.get()

        try:
            prix = float(prix)
            min_val = int(min_val)
            max_val = int(max_val)
        except ValueError:
            label_status.configure(text="Erreur : Vérifiez les valeurs", text_color="red")
            return

        cree_prod(nom, ref, categorie, fournisseur, quantite, prix, min_val, max_val)

        label_status.configure(text=f"Produit {nom} créé", text_color="blue")

        # Réinitialisation des champs
        nom_entry.delete(0, tkinter.END)
        ref_entry.delete(0, tkinter.END)
        category_menu.set(categories[0])
        supplier_menu.set(fournisseurs[0])
        quantity_var.set(1)
        price_entry.delete(0, tkinter.END)
        min_entry.delete(0, tkinter.END)
        max_entry.delete(0, tkinter.END)


    create_button = CTkButton(fields_frame, text="Créer", font=("Arial Bold", 17), command=handle_create, fg_color="green", text_color="white", corner_radius=10, height=40)
    create_button.grid(row=15, column=1, padx=20, pady=(20, 20), sticky="e")

    label_status = CTkLabel(fields_frame, text="", font=("Arial", 16), text_color="#00ff27", fg_color="transparent", bg_color="transparent")
    label_status.grid(row=15, column=0, columnspan=2, pady=(5, 15), sticky="")

def get_produits_scannes_cc():
    global produits_scannes
    return produits_scannes
def get_scan_ok():
    global scan_ok
    return scan_ok

def command(main_view):
    global produits_scannes, scan_ok, fields_frame, tree_command, user, progress_bar
    scan_ok = "ok"

    print(f"{scan_ok}")

    for widget in fields_frame.winfo_children():
        widget.destroy()
    
    CTkLabel(fields_frame, text="Création de Commande", font=("Arial Black", 25), text_color="white").pack(anchor="center", pady=20, padx=27)

    # Créer un cadre scrollable pour le tableau avec un fond blanc
    scrollable_frame = CTkScrollableFrame(fields_frame, width=1100, height=500, fg_color="white")
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


    tree_command = scrollable_frame

    CTkButton(fields_frame, text="Commander", font=("Arial", 17),
            command=lambda: process_order(user), fg_color="#207244", text_color="white").pack(pady=10)


def handle_scan_cree_command(produit_id, username):
    global mode_supp, produits_scannes, user

    user = username
    produit_id = str(produit_id)

    try:
        if mode_supp:
            produit_info = get_produit_info(produit_id)
            if produit_id in produits_scannes:
                del produits_scannes[produit_id]
                for item in tree_command.winfo_children():
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
            if not produits_scannes:
                label_status.configure(text="Aucun produit à commander.", text_color="red")
                return

            process_order(user)

        if produit_id not in ["RED001", "ACC001", "AJT001", "SCANPROD", "CONFIRM001"]:
            produit_info = get_produit_info(produit_id)
            if produit_info:
                if produit_id in produits_scannes:
                    produits_scannes[produit_id]["quantite_scannee"] += 1
                    for row in tree_command.winfo_children():
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
                    row_frame = CTkFrame(tree_command, fg_color="#f7f7f7")
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


def process_order(username):
    """Crée une commande pour chaque produit scanné avec un effet de barre de progression moderne."""
    global produits_scannes, user, progress_bar

    user = username

    if not produits_scannes:
        label_status.configure(text="Aucun produit à commander.", text_color="red")
        return

    # Création d'une barre de progression avec un design plus moderne
    progress_bar = CTkProgressBar(
        fields_frame, 
        width=300, 
        height=12, 
        corner_radius=10,  
        fg_color="#2E2E2E",  # Couleur de fond
        progress_color="#4CAF50"  # Couleur de progression (vert moderne)
    )
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    step = 1 / len(produits_scannes)

    def update_progress():
        for i, (produit_id, infos) in enumerate(produits_scannes.items(), start=1):
            time.sleep(0.5)  # Simule un délai de traitement
            
            crea_command(produit_id, infos["quantite_scannee"], user)

            # Effet progressif fluide
            for j in range(10):  # 10 petites étapes pour un remplissage progressif
                progress_bar.set((i - 1) * step + (j / 10) * step)
                time.sleep(0.05)  # Petit délai pour lisser l'animation

            fields_frame.update_idletasks()

        # Fin de la progression
        progress_bar.set(1)
        label_status.configure(text="Toutes les commandes ont été créées avec succès.", text_color="green")
        time.sleep(0.5)
        progress_bar.destroy()

    # Exécuter dans un thread pour éviter de bloquer l'interface
    threading.Thread(target=update_progress, daemon=True).start()
