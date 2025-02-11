from tkinter import *
from tkinter import ttk
from customtkinter import *
from functools import partial
from PIL import Image, ImageTk
import requests
from io import BytesIO
from fonction import list_produit, plus_list_prod, moins_list_prod, crea_command, envoie_msg_command

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

# Dictionnaires pour suivre les produits scannés
scanned_products = {}
CURRENT_PAGE = 0
ITEMS_PER_PAGE = 23  # Nombre de produits par page
pagination_frame = None  # Cadre pour les boutons de navigation
supplier_var = None
category_var = None



def show_all_products(main_view, username):
    global table_frame, username_la, filter_supplier, filter_category, list_rea, tree, products_displayed, pagination_frame, supplier_var, category_var, supplier_filter, category_filter

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

    # Liste des fournisseurs uniques
    suppliers = sorted(set(p["fournisseur"] for p in scanned_products.values()))
    suppliers.insert(0, "Tous")

    # Liste des catégories uniques
    categories = sorted(set(p["categorie"] for p in scanned_products.values()))
    categories.insert(0, "Toutes")

    # Initialiser les variables globales
    supplier_var = StringVar()
    category_var = StringVar()

    # Cadre pour les listes déroulantes de filtres
    filter_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    filter_frame.pack(fill="x", padx=20, pady=5)

    # Combobox pour le fournisseur (placé au-dessus de la colonne Fournisseur)
    supplier_var = StringVar()
    supplier_filter = ttk.Combobox(filter_frame, textvariable=supplier_var, values=suppliers, state="readonly")
    supplier_filter.pack(side="left", padx=50, pady=5, expand=True)  # Ajuster pour aligner avec la colonne
    supplier_filter.current(0)  # Sélectionner "Tous" par défaut
    supplier_filter.bind("<<ComboboxSelected>>", lambda event: filter_products())

    # Combobox pour la catégorie (placé au-dessus de la colonne Catégorie)
    category_var = StringVar()
    category_filter = ttk.Combobox(filter_frame, textvariable=category_var, values=categories, state="readonly")
    category_filter.pack(side="left", padx=50, pady=5, expand=True)  # Ajuster pour aligner avec la colonne
    category_filter.current(0)  # Sélectionner "Toutes" par défaut
    category_filter.bind("<<ComboboxSelected>>", lambda event: filter_products())

    # Bouton pour réinitialiser les filtres
    CTkButton(filter_frame, text="Réinitialiser", command=reset_filters).pack(side="left", padx=10)


    # Bloc pour afficher les produits avec Treeview
    table_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tree = create_product_table(table_frame)
    
    # Initialisation du cadre de pagination
    pagination_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    pagination_frame.pack(fill="x", padx=20, pady=10)

    
    update_product_table()  # Mise à jour initiale des produits


def filter_products():
    """Filtre les produits selon le fournisseur et la catégorie sélectionnés."""
    global supplier_var, category_var

    selected_supplier = supplier_var.get()
    selected_category = category_var.get()

    produits = list_produit()  # Récupérer tous les produits

    # Appliquer le filtre fournisseur
    if selected_supplier != "Tous":
        produits = [p for p in produits if p["fournisseur"] == selected_supplier]

    # Appliquer le filtre catégorie
    if selected_category != "Toutes":
        produits = [p for p in produits if p["categorie"] == selected_category]

    # Mettre à jour la liste des produits affichés
    global scanned_products
    scanned_products = {p["id"]: p for p in produits}
    update_product_table()

def reset_filters():
    """Réinitialise les filtres et affiche tous les produits."""
    global supplier_filter, category_filter, supplier_var, category_var  # Déclarer globalement

    supplier_filter.current(0)  # Remettre à "Tous"
    category_filter.current(0)  # Remettre à "Toutes"
    filter_products()  # Rafraîchir l'affichage



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
        background="#ff0000",  # Fond rouge pour les en-têtes
        foreground="black",     # Texte noir pour les en-têtes
        activebackground="#ff6666",  # Fond au survol
        activeforeground="white",   # Texte blanc au survol
        font=("Arial Bold", 13),
        borderwidth=1,
        relief="flat"
    )

    style.map("Treeview.Heading", background=[("active", "#ff0000")])  # Couleur au survol

    # Bordures des colonnes
    style.layout("Treeview", [
        ("Treeview.treearea", {"sticky": "nswe"})  # Supprime les bordures classiques
    ])


def create_product_table(table_frame):
    style_treeview()

    tree = ttk.Treeview(
        table_frame,
        columns=("Nom", "Fournisseur", "Catégorie", "Quantité"),
        show="headings",
        height=20,
    )
    tree.heading("Nom", text="Nom")
    tree.heading("Fournisseur", text="Fournisseur", command=lambda: sort_by_column(tree, "Fournisseur", False))
    tree.heading("Catégorie", text="Catégorie", command=lambda: sort_by_column(tree, "Catégorie", False))
    tree.heading("Quantité", text="Quantité", command=lambda: sort_by_column(tree, "Quantité", False))

    tree.column("Nom", width=200, anchor="center")
    tree.column("Fournisseur", width=150, anchor="center")
    tree.column("Catégorie", width=150, anchor="center")
    tree.column("Quantité", width=100, anchor="center")

    tree.pack(fill="both", expand=True)

    tree.bind("<<TreeviewSelect>>", on_product_select)

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

    for i, product in enumerate(products_displayed):
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


def sort_by_column(tree, col, reverse):
    """Trie le Treeview selon la colonne sélectionnée."""
    items = [(tree.set(k, col), k) for k in tree.get_children('')]
    
    try:
        # Essayer de trier comme des nombres
        items.sort(key=lambda t: int(t[0]), reverse=reverse)
    except ValueError:
        # Trier comme du texte si ce n'est pas un nombre
        items.sort(reverse=reverse)

    # Réinsérer les éléments triés
    for index, (val, k) in enumerate(items):
        tree.move(k, '', index)

    # Inverser l'ordre pour le prochain tri
    tree.heading(col, command=lambda: sort_by_column(tree, col, not reverse))



def on_product_select(event):
    """Affiche une fenêtre contextuelle avec les détails du produit et sa photo."""
    selected_item = tree.selection()
    if not selected_item:
        return

    item = tree.item(selected_item)
    values = item["values"]
    
    product_name = values[0]  # Nom du produit
    
    # Recherche du produit dans scanned_products (qui contient déjà la photo)
    product = next((p for p in scanned_products.values() if p["nom"] == product_name), None)
    if not product:
        return

    # Créer la fenêtre popup
    popup = CTkToplevel()
    popup.title("Détails du produit")
    popup.geometry("350x400")

    # Affichage des infos texte
    CTkLabel(popup, text=f"Produit: {product['nom']}", font=("Arial Bold", 16)).pack(pady=10)
    CTkLabel(popup, text=f"Quantité: {product['qte']}").pack()
    
    # Affichage de l'image (si disponible)
    photo_url = product.get("photo")
    if photo_url:
        try:
            response = requests.get(photo_url)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((150, 150))  # Redimensionner l’image
                photo = ImageTk.PhotoImage(img)

                label_img = Label(popup, image=photo, bg="white")
                label_img.image = photo  # Éviter le garbage collection
                label_img.pack(pady=10)
            else:
                CTkLabel(popup, text="Image non disponible").pack(pady=10)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
            CTkLabel(popup, text="Image non disponible").pack(pady=10)
    else:
        CTkLabel(popup, text="Pas d'image disponible").pack(pady=10)

    # Boutons d'action
    CTkButton(popup, text="Modifier", command=lambda: print(f"Modifier {product['nom']}")).pack(pady=5)
    CTkButton(popup, text="Supprimer", command=lambda: print(f"Supprimer {product['nom']}")).pack(pady=5)
    CTkButton(popup, text="Fermer", command=popup.destroy).pack(pady=10)