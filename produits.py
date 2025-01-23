from tkinter import *
from customtkinter import *
from functools import partial  # Pour utiliser partial
from fonction import list_produit, plus_list_prod, moins_list_prod, crea_command, envoie_msg_command

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"


# Dictionnaires pour suivre les produits scannés et leurs images
scanned_products = {}

def show_all_products(main_view, username):
    global table_frame, username_la, filter_supplier, filter_category, list_rea

    username_la = username

    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    # Récupérer la liste des produits
    produits = list_produit()

    scanned_products.clear()
    for p in produits:
        scanned_products[p["id"]] = p

    list_rea = []
    for p in produits:
        try:
            qte = int(p["qte"])
            mini = int(p["mini"])
            if qte <= mini:
                list_rea.append(p)
        except ValueError:
            # Si la conversion échoue, tu peux ignorer l'élément ou traiter l'erreur
            print(f"Erreur de conversion pour le produit : {p}")

    # Barre de recherche
    search_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    search_frame.pack(fill="x", padx=20, pady=10)

    search_entry = CTkEntry(search_frame, placeholder_text="Rechercher un produit...", width=300)
    search_entry.pack(side="left", padx=10, pady=10)

    search_entry.bind("<Return>", lambda event: search_product(search_entry.get(), table_frame))
    search_button = CTkButton(search_frame, text="Rechercher", command=lambda: search_product(search_entry.get(), table_frame))
    search_button.pack(side="left", padx=10)

    search_button = CTkButton(search_frame, text="Produits à commander", command=lambda: afficher_rea(list_rea, table_frame, username_la))
    search_button.pack(side="left", padx=10)

    # Bloc d'informations générales
    info_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    # Informations (placeholders)
    info_labels = [
        ("Total Produits", len(produits) if produits else 0),
        ("Nombre Fournisseurs", len(set(p["fournisseur"] for p in produits))),
        ("Catégories", len(set(p["categorie"] for p in produits))),
        ("Produits à commander", len(list_rea)),
        ("Articles en Rupture", sum(1 for p in produits if p["qte"] == 0))
    ]

    for i, (label, value) in enumerate(info_labels):
        info_block = CTkFrame(info_frame, fg_color="#FFFFFF", corner_radius=10, width=120, height=80)
        info_block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        CTkLabel(info_block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR).pack(pady=5)
        CTkLabel(info_block, text=label, font=("Arial", 20), text_color=TEXT_COLOR).pack()

    # Bloc pour afficher les produits avec scrollbar
    scrollable_frame = CTkScrollableFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Tableau des produits
    table_frame = CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Créer les en-têtes
    filter_supplier = StringVar(value="Tous")
    filter_category = StringVar(value="Tous")
    create_table_headers(table_frame, produits)

    # Ajouter les produits dans la liste
    update_product_table(produits, table_frame, username_la)


def create_table_headers(table_frame, products):
    """Crée les en-têtes de colonnes pour la table des produits avec un bandeau gris clair."""
    headers = ["Nom", "Fournisseur", "Catégorie", "Quantité", "Actions"]
    suppliers = ["Tous"] + sorted(set(p["fournisseur"] for p in products))
    categories = ["Tous"] + sorted(set(p["categorie"] for p in products))

    # Ajouter un bandeau gris clair sous les en-têtes (en utilisant un Label)
    header_bg_label = CTkLabel(
        table_frame,
        text=" " * 100,  # L'important est de faire un label large
        fg_color="#d3d3d3",  # Fond gris clair
        width=10000,  # Largeur importante pour couvrir toute la zone
        height=30  # Hauteur de la ligne d'en-tête
    )
    header_bg_label.grid(row=0, column=0, columnspan=len(headers), sticky="nsew")

    # Configurer les colonnes
    for col, header in enumerate(headers):
        if header == "Actions":
            table_frame.grid_columnconfigure(col, minsize=70, weight=0)  # Largeur fixe pour Actions
        else:
            table_frame.grid_columnconfigure(col, weight=1)  # Colonnes extensibles pour les autres

        # Ajouter les cadres d'en-tête avec fond transparent
        header_frame = CTkFrame(
            table_frame,
            fg_color="transparent",  # Transparent pour laisser voir le fond gris clair
            corner_radius=8
        )
        header_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        header_frame.tag = "header"

        # Ajouter les menus déroulants pour Fournisseur et Catégorie
        if header == "Fournisseur":
            filter_menu = CTkOptionMenu(
                header_frame, values=suppliers, variable=filter_supplier,
                command=lambda _: filter_products()
            )
            filter_menu.pack(fill="x", padx=5, pady=5)
        elif header == "Catégorie":
            filter_menu = CTkOptionMenu(
                header_frame, values=categories, variable=filter_category,
                command=lambda _: filter_products()
            )
            filter_menu.pack(fill="x", padx=5, pady=5)
        else:
            # Ajouter une étiquette pour les autres colonnes
            header_label = CTkLabel(
                header_frame,
                text=header,
                font=("Arial Bold", 20),
                text_color="#333333"  # Couleur du texte foncé pour contraster avec le gris clair
            )
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
        if product in list_rea:

            CTkLabel(
                table_frame, text=product["nom"], font=("Arial", 16), text_color="red"
            ).grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
            CTkLabel(
                table_frame, text=product["fournisseur"], font=("Arial", 16), text_color="red"
            ).grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
            CTkLabel(
                table_frame, text=product["categorie"], font=("Arial", 16), text_color="red"
            ).grid(row=row, column=2, padx=5, pady=5, sticky="nsew")
            quantity_label = CTkLabel(
                table_frame, text=str(product["qte"]), font=("Arial", 16), text_color="red"
            )
            quantity_label.grid(row=row, column=3, padx=5, pady=5, sticky="nsew")
        else:

            CTkLabel(
                table_frame, text=product["nom"], font=("Arial", 16), text_color=TEXT_COLOR
            ).grid(row=row, column=0, padx=5, pady=5, sticky="nsew")
            CTkLabel(
                table_frame, text=product["fournisseur"], font=("Arial", 16), text_color=TEXT_COLOR
            ).grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
            CTkLabel(
                table_frame, text=product["categorie"], font=("Arial", 16), text_color=TEXT_COLOR
            ).grid(row=row, column=2, padx=5, pady=5, sticky="nsew")
            quantity_label = CTkLabel(
                table_frame, text=str(product["qte"]), font=("Arial", 16), text_color=TEXT_COLOR
            )
            quantity_label.grid(row=row, column=3, padx=5, pady=5, sticky="nsew")


        product["quantity_label"] = quantity_label

        action_frame = CTkFrame(table_frame, fg_color="transparent")
        action_frame.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")
        CTkButton(
            action_frame, text="+", width=30, command=partial(increment_quantity, product, username)
        ).pack(side="left", padx=5)
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
            table_frame, text=product["fournisseur"], font=("Arial", 16), text_color="red"
        ).grid(row=row, column=1, padx=5, pady=5, sticky="nsew")
        CTkLabel(
            table_frame, text=product["categorie"], font=("Arial", 16), text_color="red"
        ).grid(row=row, column=2, padx=5, pady=5, sticky="nsew")
        quantity_label = CTkLabel(
            table_frame, text=str(product["qte"]), font=("Arial", 16), text_color="red"
        )
        quantity_label.grid(row=row, column=3, padx=5, pady=5, sticky="nsew")

        product["quantity_label"] = quantity_label

        action_frame = CTkFrame(table_frame, fg_color="transparent")
        action_frame.grid(row=row, column=4, padx=5, pady=5, sticky="nsew")
        CTkButton(action_frame, text="Commander", width=60, command=partial(command, product, username)).pack(side="left", padx=5)


def increment_quantity(product, username):
    """Incrémente la quantité du produit."""
    success = plus_list_prod(product["id"], username)
    if success:
        product["qte"] += 1
        product["quantity_label"].configure(text=str(product["qte"]))


def decrement_quantity(product, username):
    """Décrémente la quantité du produit."""
    if product["qte"] > 0:
        success = moins_list_prod(product["id"], username)
        if success:
            product["qte"] -= 1
            product["quantity_label"].configure(text=str(product["qte"]))

def command(product, username):

    qte = product["max"] - product["qte"]
    message = f"Produit à commander : \n\n - {product['nom']} : {qte} unités\n"

    crea_command(product["id"], qte, username)
    envoie_msg_command(message)
