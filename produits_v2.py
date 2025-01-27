from tkinter import *
from tkinter import ttk
from customtkinter import *
from functools import partial
from fonction import list_produit, plus_list_prod, moins_list_prod, crea_command, envoie_msg_command

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

# Dictionnaires pour suivre les produits scannés
scanned_products = {}
CURRENT_PAGE = 0
ITEMS_PER_PAGE = 24  # Nombre de produits par page
pagination_frame = None  # Cadre pour les boutons de navigation


def show_all_products(main_view, username):
    global table_frame, username_la, filter_supplier, filter_category, list_rea, tree, products_displayed, pagination_frame

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
            print(f"Erreur de conversion pour le produit : {p}")

    # Barre de recherche
    search_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    search_frame.pack(fill="x", padx=20, pady=10)

    search_entry = CTkEntry(search_frame, placeholder_text="Rechercher un produit...", width=300)
    search_entry.pack(side="left", padx=10, pady=10)

    search_entry.bind("<Return>", lambda event: search_product(search_entry.get()))
    search_button = CTkButton(search_frame, text="Rechercher", command=lambda: search_product(search_entry.get()))
    search_button.pack(side="left", padx=10)

    CTkButton(search_frame, text="Produits à commander", command=lambda: afficher_rea()).pack(side="left", padx=10)

    # Bloc d'informations générales
    info_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    info_labels = [
        ("Total Produits", len(produits)),
        ("Nombre Fournisseurs", len(set(p["fournisseur"] for p in produits))),
        ("Catégories", len(set(p["categorie"] for p in produits))),
        ("Produits à commander", len(list_rea)),
        ("Articles en Rupture", sum(1 for p in produits if p["qte"] == 0))
    ]

    for label, value in info_labels:
        info_block = CTkFrame(info_frame, fg_color="#FFFFFF", corner_radius=10, width=120, height=80)
        info_block.pack(side="left", padx=10, pady=10, expand=True, fill="both")
        CTkLabel(info_block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR).pack(pady=5)
        CTkLabel(info_block, text=label, font=("Arial", 20), text_color=TEXT_COLOR).pack()

    # Bloc pour afficher les produits avec Treeview
    table_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tree = create_product_table(table_frame)
    
    # Initialisation du cadre de pagination
    pagination_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    pagination_frame.pack(fill="x", pady=10)
    
    update_product_table()  # Mise à jour initiale des produits

def style_treeview():
    """Applique un style moderne au Treeview."""
    style = ttk.Style()

    # Configuration générale du Treeview
    style.configure(
        "Treeview",
        background="#F7F9FB",  # Couleur de fond
        foreground="#333333",  # Couleur du texte
        rowheight=30,  # Hauteur des lignes
        fieldbackground="#F7F9FB",  # Couleur de fond alternative
        font=("Arial", 12)  # Police du texte
    )

    # Style des en-têtes
    style.configure(
        "Treeview.Heading",
        background="#2A8C55",  # Couleur de fond des en-têtes
        foreground="black",  # Couleur du texte des en-têtes
        font=("Arial Bold", 13),  # Police des en-têtes
        borderwidth=1,
        relief="flat"  # Supprime les bordures épaisses classiques
    )
    style.map("Treeview.Heading", background=[("active", "#238645")])  # Couleur au survol

    # Bordures des colonnes
    style.layout("Treeview", [
        ("Treeview.treearea", {"sticky": "nswe"})  # Supprime les bordures classiques
    ])


def create_product_table(table_frame):
    """Crée une table virtuelle pour afficher les produits."""

    style_treeview()

    tree = ttk.Treeview(
        table_frame,
        columns=("Nom", "Fournisseur", "Catégorie", "Quantité"),
        show="headings",
        height=20
    )
    tree.heading("Nom", text="Nom")
    tree.heading("Fournisseur", text="Fournisseur")
    tree.heading("Catégorie", text="Catégorie")
    tree.heading("Quantité", text="Quantité")

    tree.column("Nom", width=200, anchor="center")
    tree.column("Fournisseur", width=150, anchor="center")
    tree.column("Catégorie", width=150, anchor="center")
    tree.column("Quantité", width=100, anchor="center")

    tree.pack(fill="both", expand=True)
    return tree


def update_product_table(page=0):
    """Met à jour uniquement les lignes visibles de la table."""
    global CURRENT_PAGE, products_displayed

    CURRENT_PAGE = page

    # Effacer les anciennes données
    tree.delete(*tree.get_children())

    # Récupérer les produits à afficher pour la page actuelle
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    products_displayed = list(scanned_products.values())[start_index:end_index]

    for product in products_displayed:
        row_color = "red" if product in list_rea else "black"
        tree.insert(
            "",
            "end",
            values=(product["nom"], product["fournisseur"], product["categorie"], product["qte"]),
            tags=(row_color,)
        )

    # Configurer les couleurs
    tree.tag_configure("red", foreground="red")
    tree.tag_configure("black", foreground="black")

    # Mettre à jour les boutons de navigation
    update_pagination_controls()


def update_pagination_controls():
    """Met à jour les boutons de navigation pour les pages."""
    global pagination_frame

    if pagination_frame is None:
        print("Erreur : pagination_frame n'a pas été initialisé.")
        return

    # Nettoyer le cadre pour éviter les doublons
    for widget in pagination_frame.winfo_children():
        widget.destroy()

    total_pages = (len(scanned_products) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    if CURRENT_PAGE > 0:
        CTkButton(pagination_frame, text="Précédent", command=lambda: update_product_table(CURRENT_PAGE - 1)).pack(side="left", padx=10)

    if CURRENT_PAGE < total_pages - 1:
        CTkButton(pagination_frame, text="Suivant", command=lambda: update_product_table(CURRENT_PAGE + 1)).pack(side="right", padx=10)


def search_product(query):
    """Recherche un produit."""
    global scanned_products

    query = query.strip().lower()

    if query == "":
        # Si la recherche est vide, réinitialiser à tous les produits
        scanned_products = {p["id"]: p for p in list_produit()}
    else:
        # Filtrer les produits selon la requête
        scanned_products = {
            p["id"]: p for p in list_produit()
            if query in p["nom"].lower() or query in p["fournisseur"].lower() or query in p["categorie"].lower()
        }

    # Mettre à jour l'affichage avec les produits filtrés
    update_product_table()



def afficher_rea():
    """Filtre les produits à recommander."""
    global scanned_products

    scanned_products = {p["id"]: p for p in list_rea}
    update_product_table()
