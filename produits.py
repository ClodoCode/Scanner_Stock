from tkinter import *
from customtkinter import *
from functools import partial  # Pour utiliser partial
from fonction import list_produit, plus_list_prod, moins_list_prod, crea_command, envoie_msg_command
import time
import threading

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

scanned_products = {}
list_rea = []

def show_all_products(main_view, username):
    """Affiche tous les produits avec chargement optimisé."""
    global table_frame, username_la, filter_supplier, filter_category, list_rea, loading_in_progress
    username_la = username

    # Supprimer les anciens widgets
    for widget in main_view.winfo_children():
        widget.destroy()

    # Définir les filtres globaux
    filter_supplier = StringVar(value="Tous")
    filter_category = StringVar(value="Tous")

    # Barre de recherche + Filtrage
    search_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    search_frame.pack(fill="x", padx=20, pady=10)

    search_entry = CTkEntry(search_frame, placeholder_text="Rechercher un produit...", width=300)
    search_entry.pack(side="left", padx=10, pady=10)

    search_button = CTkButton(search_frame, text="Rechercher", command=lambda: search_product(search_entry.get(), table_frame))
    search_button.pack(side="left", padx=10)

    prod_rea_button = CTkButton(search_frame, text="Produits à commander", command=lambda: afficher_rea(list_rea, table_frame, username_la))
    prod_rea_button.pack(side="left", padx=10)

    refresh_button = CTkButton(search_frame, text="🔄 Actualiser", command=lambda: load_products(main_view, table_frame, True))
    refresh_button.pack(side="right", padx=10)

    # Zone des informations
    info_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    info_labels = [
        ("Total Produits", "0"),
        ("Nombre Fournisseurs", "0"),
        ("Catégories", "0"),
        ("Produits à commander", "0"),
        ("Articles en Rupture", "0")
    ]
    
    info_blocks = []
    for label, value in info_labels:
        block = CTkFrame(info_frame, fg_color="#FFFFFF", corner_radius=10, width=120, height=80)
        block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        value_label = CTkLabel(block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR)
        value_label.pack(pady=5)
        CTkLabel(block, text=label, font=("Arial", 20), text_color=TEXT_COLOR).pack()
        info_blocks.append(value_label)  # Stocker les labels pour MAJ plus tard

    # Zone de scroll pour la liste des produits
    scrollable_frame = CTkScrollableFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    table_frame = CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ✅ Charger les produits UNE SEULE FOIS pour éviter les répétitions
    if not loading_in_progress:
        loading_in_progress = True
        threading.Thread(target=load_products, args=(main_view, table_frame, info_blocks), daemon=True).start()


def load_products(main_view, table_frame, info_blocks=None, force_reload=False):
    """Charge les produits en arrière-plan avec affichage progressif et évite les doublons."""
    global scanned_products, list_rea, loading_in_progress

    # Charger les produits depuis la base de données
    produits = list_produit()
    scanned_products.clear()
    
    for p in produits:
        scanned_products[p["id"]] = p

    # Déterminer les produits à commander
    list_rea = [p for p in produits if int(p["qte"]) < int(p["mini"])]

    # Mettre à jour les infos générales
    if info_blocks:
        info_blocks[0].configure(text=str(len(produits)))  # Total Produits
        info_blocks[1].configure(text=str(len(set(p["fournisseur"] for p in produits))))  # Fournisseurs
        info_blocks[2].configure(text=str(len(set(p["categorie"] for p in produits))))  # Catégories
        info_blocks[3].configure(text=str(len(list_rea)))  # Produits à commander
        info_blocks[4].configure(text=str(sum(1 for p in produits if int(p["qte"]) == 0)))  # Ruptures

    # Supprimer l'ancien contenu
    for widget in table_frame.winfo_children():
        widget.destroy()

    # Créer les en-têtes avec la colonne "Actions" bien dimensionnée
    create_table_headers(table_frame, produits)

    # Charger les produits en lots pour éviter les blocages
    def load_batch(start=0, batch_size=15):
        end = min(start + batch_size, len(produits))
        update_product_table(produits[start:end], table_frame, username_la)

        if end < len(produits):
            main_view.after(50, load_batch, end)  # Chargement progressif
        else:
            loading_in_progress = False  # ✅ Définir comme terminé

    # Lancer le chargement progressif
    main_view.after(50, load_batch, 0)



def create_table_headers(table_frame, products):
    """Crée les en-têtes de colonnes pour la table des produits avec un bandeau gris clair."""
    global filter_supplier, filter_category  # Ajout de cette ligne

    headers = ["Nom", "Réf", "Fournisseur", "Catégorie", "Qte", "Actions"]
    suppliers = ["Tous"] + sorted(set(p["fournisseur"] for p in products))
    categories = ["Tous"] + sorted(set(p["categorie"] for p in products))

    # Ajouter un bandeau gris clair sous les en-têtes
    header_bg_label = CTkLabel(
        table_frame,
        text=" " * 100,
        fg_color="#d3d3d3",
        width=10000,
        height=30
    )
    header_bg_label.grid(row=0, column=0, columnspan=len(headers), sticky="nsew")

    # Configurer les colonnes
    for col, header in enumerate(headers):
        table_frame.grid_columnconfigure(col, weight=1)

        header_frame = CTkFrame(table_frame, fg_color="transparent", corner_radius=8)
        header_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        header_frame.tag = "header"

        # Ajouter les menus déroulants pour Fournisseur et Catégorie
        if header == "Fournisseur":
            filter_menu = CTkOptionMenu(header_frame, values=suppliers, variable=filter_supplier, command=lambda _: filter_products())
            filter_menu.pack(fill="x", padx=5, pady=5)
        elif header == "Catégorie":
            filter_menu = CTkOptionMenu(header_frame, values=categories, variable=filter_category, command=lambda _: filter_products())
            filter_menu.pack(fill="x", padx=5, pady=5)
        else:
            header_label = CTkLabel(header_frame, text=header, font=("Arial Bold", 20), text_color="#333333")
            header_label.pack(padx=10, pady=10)



def filter_products():
    """Filtre les produits selon les critères sélectionnés."""
    filtered = list(scanned_products.values())
    if filter_supplier.get() != "Tous":
        filtered = [p for p in filtered if p["fournisseur"] == filter_supplier.get()]
    if filter_category.get() != "Tous":
        filtered = [p for p in filtered if p["categorie"] == filter_category.get()]
    update_product_table(filtered, table_frame, username_la)


def search_product(query, table_frame):
    """Recherche un produit en tenant compte des filtres actifs (fournisseur, catégorie)."""
    
    # Filtrer les produits en fonction des filtres de fournisseur et catégorie
    filtered_products = list(scanned_products.values())  # Démarrer avec tous les produits scannés
    
    # Appliquer le filtre de fournisseur
    if filter_supplier.get() != "Tous":
        filtered_products = [p for p in filtered_products if p["fournisseur"] == filter_supplier.get()]
    
    # Appliquer le filtre de catégorie
    if filter_category.get() != "Tous":
        filtered_products = [p for p in filtered_products if p["categorie"] == filter_category.get()]

    # Filtrer par la recherche du nom, fournisseur ou catégorie
    query = query.strip().lower()
    filtered_products = [
        p for p in filtered_products
        if query in p["nom"].lower() or query in p["fournisseur"].lower() or query in p["categorie"].lower()
    ]

    # Mettre à jour la table avec les produits filtrés et recherchés
    update_product_table(filtered_products, table_frame, username_la)



def update_product_table(products, table_frame, username):
    """Met à jour uniquement les lignes des produits dans la table."""
    for widget in table_frame.winfo_children():
        if getattr(widget, "tag", None) != "header":
            widget.destroy()

    for row, product in enumerate(products, start=1):
        # Définir la couleur du texte selon si le produit est dans list_rea ou non
        text_color = "red" if product in list_rea else TEXT_COLOR

        # Créer les labels et les ajouter à la table
        name_label = CTkLabel(
            table_frame, text=product["nom"], font=("Arial", 16), text_color=text_color
        )
        name_label.grid(row=row, column=0, padx=5, pady=5, sticky="nsew")

        ref_label = CTkLabel(
            table_frame, text=product["ref"], font=("Arial", 16), text_color=text_color
        )
        ref_label.grid(row=row, column=1, padx=5, pady=5, sticky="nsew")

        fournisseur_label = CTkLabel(
            table_frame, text=product["fournisseur"], font=("Arial", 16), text_color=text_color
        )
        fournisseur_label.grid(row=row, column=2, padx=5, pady=5, sticky="nsew")

        categorie_label = CTkLabel(
            table_frame, text=product["categorie"], font=("Arial", 16), text_color=text_color
        )
        categorie_label.grid(row=row, column=3, padx=5, pady=5, sticky="nsew")

        quantity_label = CTkLabel(
            table_frame, text=str(product["qte"]), font=("Arial", 16), text_color=text_color
        )
        quantity_label.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")

        # Ajouter les labels au dictionnaire `product`
        product["name_label"] = name_label
        product["ref_label"] = ref_label
        product["quantity_label"] = quantity_label
        product["fournisseur_label"] = fournisseur_label
        product["categorie_label"] = categorie_label


        # Cadre pour les actions (+ et -)
        action_frame = CTkFrame(table_frame, fg_color="transparent")
        action_frame.grid(row=row, column=5, padx=5, pady=5, sticky="nsew")
        
        # Bouton +
        CTkButton(
            action_frame, text="+", width=30, command=partial(increment_quantity, product, username)
        ).pack(side="left", padx=5)
        
        # Bouton -
        CTkButton(
            action_frame, text="-", width=30, command=partial(decrement_quantity, product, username)
        ).pack(side="right", padx=5)


def afficher_rea(products, table_frame, username):
    """Met à jour uniquement les lignes des produits dans la table."""
    for widget in table_frame.winfo_children():
        if getattr(widget, "tag", None) != "header":
            widget.destroy()

    for row, product in enumerate(products, start=1):

        CTkLabel(
            table_frame, text=product["nom"], font=("Arial", 16), text_color="red"
        ).grid(row=row, column=0, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            table_frame, text=product["ref"], font=("Arial", 16), text_color="red"
        ).grid(row=row, column=1, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            table_frame, text=product["fournisseur"], font=("Arial", 16), text_color="red"
        ).grid(row=row, column=2, padx=5, pady=5, sticky="nsew")

        CTkLabel(
            table_frame, text=product["categorie"], font=("Arial", 16), text_color="red"
        ).grid(row=row, column=3, padx=5, pady=5, sticky="nsew")

        quantity_label = CTkLabel(
            table_frame, text=str(product["qte"]), font=("Arial", 16), text_color="red"
        )
        quantity_label.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")

        product["quantity_label"] = quantity_label

        action_frame = CTkFrame(table_frame, fg_color="transparent")
        action_frame.grid(row=row, column=5, padx=5, pady=5, sticky="nsew")
        CTkButton(action_frame, text="Commander", width=60, command=partial(command, product, username)).pack(side="left", padx=5)


def increment_quantity(product, username):
    """Incrémente la quantité du produit."""
    success = plus_list_prod(product["id"], username)
    if success:
        product["qte"] += 1
        product["quantity_label"].configure(text=str(product["qte"]))

        # Vérifier si le produit n'est plus en faible stock
        if not is_low_stock(product) and product in list_rea:
            list_rea.remove(product)  # Retirer de la liste des produits à commander
            product["name_label"].configure(text_color=TEXT_COLOR)  # Mettre en noir
            product["ref_label"].configure(text_color=TEXT_COLOR)  # Mettre en noir
            product["fournisseur_label"].configure(text_color=TEXT_COLOR)
            product["categorie_label"].configure(text_color=TEXT_COLOR)
            product["quantity_label"].configure(text_color=TEXT_COLOR)


def decrement_quantity(product, username):
    """Décrémente la quantité du produit."""
    if product["qte"] > 0:
        success = moins_list_prod(product["id"], username)
        if success:
            product["qte"] -= 1
            product["quantity_label"].configure(text=str(product["qte"]))

            # Vérifier si le produit est désormais en faible stock
            if is_low_stock(product) and product not in list_rea:
                list_rea.append(product)  # Ajouter à la liste des produits à commander
                product["name_label"].configure(text_color="red")  # Mettre en rouge
                product["ref_label"].configure(text_color="red")  # Mettre en noir
                product["fournisseur_label"].configure(text_color="red")
                product["categorie_label"].configure(text_color="red")
                product["quantity_label"].configure(text_color="red")



def is_low_stock(product):

    try:
        qte = int(product["qte"])  # Quantité actuelle
        mini = int(product["mini"])  # Quantité minimale
        return qte <= mini
    except (KeyError, ValueError):
        # Retourne False si les clés "qte" ou "mini" n'existent pas ou si leur conversion échoue
        print(f"Erreur dans les données du produit : {product}")
        return False



def command(product, username):

    qte = product["max"] - product["qte"]
    message = f"Produit à commander : \n\n - {product['nom']} : {qte} unités\n"

    crea_command(product["id"], qte, username)
    envoie_msg_command(message)
