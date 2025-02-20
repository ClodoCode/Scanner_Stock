from tkinter import *
from tkinter import ttk
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from functools import partial
from PIL import Image, ImageTk
import requests
import time
import threading
from io import BytesIO
from ctypes import windll
from fonction import list_produit, crea_command, envoie_msg_command, mov_prod, update_product

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

# Dictionnaires pour suivre les produits scannés
scanned_products = {}
all_products = []
CURRENT_PAGE = 0
ITEMS_PER_PAGE = 23  # Nombre de produits par page
pagination_frame = None  # Cadre pour les boutons de navigation
supplier_var = None
category_var = None

windll.shcore.SetProcessDpiAwareness(1)

def get_screen_scale():
    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # Vérification du facteur d'échelle DPI
    if screen_width > 2500:  # Résolution > 2500px = écran haute résolution (Surface Pro)
        return 1.20  # Facteur d'échelle 200%
    else:
        return 1  # Facteur d'échelle 100% (écran classique)

def get_screen_scale_police():
    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # Vérification du facteur d'échelle DPI
    if screen_width > 2500:  # Résolution > 2500px = écran haute résolution (Surface Pro)
        return 1.1  # Facteur d'échelle 200%
    else:
        return 1  # Facteur d'échelle 100% (écran classique)

SCALE_FACTOR = get_screen_scale()
SCALE_FACTOR_POLICE = get_screen_scale_police()

def show_all_products(main_view, username):
    global table_frame, username_la, filter_supplier, filter_category, list_rea, tree, products_displayed, pagination_frame, supplier_var, category_var, supplier_filter, category_filter, all_products, info_labels

    username_la = username
    all_products = list_produit()  # Charge une seule fois les produits
    scanned_products = {p["id"]: p for p in all_products}

    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()


    # 📌 Ajout de la barre de chargement
    loading_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    loading_frame.pack(fill="x", padx=20, pady=10)
    
    loading_label = CTkLabel(loading_frame, text="Chargement des produits...", font=("Arial", 16))
    loading_label.pack(pady=5)

    progress_bar = CTkProgressBar(loading_frame)
    progress_bar.pack(fill="x", padx=20, pady=5)
    progress_bar.set(0)  # Initialiser la barre

    main_view.update()  # Mise à jour de l'UI pour afficher la barre immédiatement

    # 📌 Simuler le chargement progressif
    for i in range(1, 101, 10):
        progress_bar.set(i / 100)
        main_view.update()
        time.sleep(0.1)  # Petite pause pour montrer la progression

    # Récupérer la liste des produits
    produits = list_produit()

    list_rea = []
    for p in produits:
        try:
            qte = int(p["qte"])
            mini = int(p["mini"])
            if qte < mini:
                list_rea.append(p)
        except ValueError:
            print(f"Erreur de conversion pour le produit : {p}")


    # Supprimer la barre de chargement après chargement
    loading_frame.destroy()

    # Barre de recherche
    search_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    search_frame.pack(fill="x", padx=20, pady=10)

    search_entry = CTkEntry(search_frame, placeholder_text="Rechercher un produit...", width=300)
    search_entry.pack(side="left", padx=10, pady=10)

    search_entry.bind("<Return>", lambda event: search_product(search_entry.get()))
    search_button = CTkButton(search_frame, text="Rechercher", command=lambda: search_product(search_entry.get()))
    search_button.pack(side="left", padx=10)

    CTkButton(search_frame, text="Produits à commander", command=lambda: afficher_rea()).pack(side="left", padx=10)

    # Ajout du séparateur "|"
    CTkLabel(search_frame, text="|", font=("Arial", 16), text_color=TEXT_COLOR).pack(side="left", padx=5)

    # Ajout des boutons de filtrage par lieu
    CTkButton(search_frame, text="STOCK", command=lambda: filter_by_location("STOCK")).pack(side="left", padx=5)
    CTkButton(search_frame, text="TENTE", command=lambda: filter_by_location("TENTE")).pack(side="left", padx=5)
    CTkButton(search_frame, text="BUREAU", command=lambda: filter_by_location("BUREAU")).pack(side="left", padx=5)
    CTkButton(search_frame, text="CHAPITOT", command=lambda: filter_by_location("CHAPITOT")).pack(side="left", padx=5)


    # Bloc d'informations générales
    info_frame = CTkFrame(main_view, fg_color=BG_COLOR, corner_radius=15)
    info_frame.pack(fill="x", padx=20, pady=10)

    # Liste pour stocker les labels des bulles d'info
    info_labels = []

    # Création des bulles d'informations
    info_labels_data = [
        ("Total Produits", len(produits)),
        ("Nombre Fournisseurs", len(set(p["fournisseur"] for p in produits))),
        ("Catégories", len(set(p["categorie"] for p in produits))),
        ("Produits à commander", len(list_rea)),
        ("Articles en Rupture", sum(1 for p in produits if int(p["qte"]) == 0))
    ]

    for label, value in info_labels_data:
        info_block = CTkFrame(info_frame, fg_color="#FFFFFF", corner_radius=10, width=120, height=80)
        info_block.pack(side="left", padx=10, pady=10, expand=True, fill="both")

        value_label = CTkLabel(info_block, text=str(value), font=("Arial Bold", 25), text_color=HIGHLIGHT_COLOR)
        value_label.pack(pady=5)

        CTkLabel(info_block, text=label, font=("Arial", 20), text_color=TEXT_COLOR).pack()

        info_labels.append(value_label)  # Stocke les références des labels


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
    filter_products()


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
    
def filter_by_location(location):
    """Filtre les produits en fonction de leur lieu de stockage."""
    global scanned_products
    scanned_products = {p["id"]: p for p in all_products if p.get("lieu", "") == location}
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
        rowheight=int(30 * SCALE_FACTOR * SCALE_FACTOR * SCALE_FACTOR),  # Hauteur des lignes
        fieldbackground="#F7F9FB",  # Couleur de fond alternative
        font=("Arial", int(12))  # Police du texte
    )

    # Style des en-têtes
    style.configure(
        "Treeview.Heading",
        background="#ff0000",
        foreground="black",   
        activebackground="#ff6666",
        rowheight=int(30 * SCALE_FACTOR),
        activeforeground="white",
        font=("Arial", int(13 * SCALE_FACTOR)),
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
        columns=("Nom", "Référence", "Fournisseur", "Catégorie", "Quantité"),
        show="headings",
        height=20,
    )
    tree.heading("Nom", text="Nom")
    tree.heading("Référence", text="Référence")
    tree.heading("Fournisseur", text="Fournisseur", command=lambda: sort_by_column(tree, "Fournisseur", False))
    tree.heading("Catégorie", text="Catégorie", command=lambda: sort_by_column(tree, "Catégorie", False))
    tree.heading("Quantité", text="Quantité", command=lambda: sort_by_column(tree, "Quantité", False))

    tree.column("Nom", width=int(200 * SCALE_FACTOR), anchor="center")
    tree.column("Référence", width=int(110 * SCALE_FACTOR), anchor="center")
    tree.column("Fournisseur", width=int(110 * SCALE_FACTOR), anchor="center")
    tree.column("Catégorie", width=int(110 * SCALE_FACTOR), anchor="center")
    tree.column("Quantité", width=int(75 * SCALE_FACTOR), anchor="center")

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
            values=(product["nom"], product["ref"], product["fournisseur"], product["categorie"], product["qte"]),
            tags=(row_color,)
        )


    # Configurer les couleurs
    tree.tag_configure("red", foreground="red")
    tree.tag_configure("black", foreground="black")

    # Mettre à jour les boutons de navigation
    update_pagination_controls()

def update_product_quantity(product_id, new_quantity):
    """Met à jour la quantité affichée pour un produit et ajuste la couleur si nécessaire."""
    global list_rea

    for item in tree.get_children():
        values = tree.item(item, "values")
        if values[0] == scanned_products[product_id]["nom"]:
            # Mise à jour des données locales
            scanned_products[product_id]["qte"] = new_quantity

            # Vérifier si le produit doit être dans la liste des réapprovisionnements
            mini_quantity = int(scanned_products[product_id]["mini"])
            if new_quantity < mini_quantity and product_id not in [p["id"] for p in list_rea]:
                list_rea.append(scanned_products[product_id])  # Ajouter à la liste de réapprovisionnement
                tree.item(item, values=(values[0], values[1], values[2], values[3], new_quantity), tags=("red",))
            else:
                if product_id in [p["id"] for p in list_rea] and new_quantity >= mini_quantity:
                    list_rea = [p for p in list_rea if p["id"] != product_id]  # Retirer de la liste
                tree.item(item, values=(values[0], values[1], values[2], values[3], new_quantity), tags=("black",))

            break

    # Mise à jour des couleurs et des bulles d'info
    tree.tag_configure("red", foreground="red")
    tree.tag_configure("black", foreground="black")
    update_info_bubbles()  # 🔥 Ajout de cette ligne pour mettre à jour les bulles


def update_info_bubbles():
    """Met à jour les bulles d'information affichées au-dessus du tableau après chaque modification."""
    global list_rea, info_labels

    # 🔥 Rafraîchir la liste des produits à recommander avant de mettre à jour les bulles
    refresh_list_rea()

    total_products = len(scanned_products)
    total_suppliers = len(set(p["fournisseur"] for p in scanned_products.values()))
    total_categories = len(set(p["categorie"] for p in scanned_products.values()))
    total_restock = len(list_rea)  # Nombre de produits à commander (maintenant toujours à jour)
    total_out_of_stock = sum(1 for p in scanned_products.values() if int(p["qte"]) == 0)

    # Vérifier que info_labels est bien initialisé
    if len(info_labels) < 5:
        print("Erreur: info_labels n'est pas bien initialisé")
        return

    # Mise à jour des bulles d'information
    info_labels[0].configure(text=f"{total_products}")
    info_labels[1].configure(text=f"{total_suppliers}")
    info_labels[2].configure(text=f"{total_categories}")
    info_labels[3].configure(text=f"{total_restock}")
    info_labels[4].configure(text=f"{total_out_of_stock}")



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

def refresh_list_rea():
    """Met à jour la liste des produits à commander en fonction des quantités actuelles."""
    global list_rea
    list_rea = [p for p in scanned_products.values() if int(p["qte"]) < int(p["mini"])]

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
    items = [(tree.set(k, col), k) for k in tree.get_children('')]

    try:
        items.sort(key=lambda t: float(t[0]) if t[0].isdigit() else t[0].lower(), reverse=reverse)
    except ValueError:
        items.sort(key=lambda t: t[0].lower(), reverse=reverse)

    for index, (val, k) in enumerate(items):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_by_column(tree, col, not reverse))


def on_product_select(event):
    """Affiche une fenêtre contextuelle avec les détails du produit et sa photo."""
    selected_item = tree.selection()
    if not selected_item:
        return

    item = tree.item(selected_item)
    values = item["values"]
    product_name = values[0]  # Nom du produit

    # Recherche du produit
    product = next((p for p in scanned_products.values() if p["nom"] == product_name), None)
    if not product:
        return

    # Création de la fenêtre popup
    popup = CTkToplevel()
    popup.title("Détails du produit")
    popup.geometry("550x500")
    popup.resizable(False, False)
    popup.protocol("WM_DELETE_WINDOW", lambda: popup.withdraw())  # Empêcher la fermeture accidentelle

    # Affichage des informations produit
    CTkLabel(popup, text=f"Produit: {product['nom']}", font=("Arial Bold", 16)).pack(pady=10)
    CTkLabel(popup, text=f"Quantité: {product['qte']}").pack()

    # Chargement de l'image du produit
    def load_product_image(photo_url):
        if not photo_url or not photo_url.startswith("http"):
            return None
        try:
            response = requests.get(photo_url, timeout=5)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data).resize((150, 150))
            return ImageTk.PhotoImage(img)
        except requests.RequestException as e:
            print(f"Erreur de chargement de l'image: {e}")
        return None

    photo = load_product_image(product.get("photo"))
    if photo:
        label_img = Label(popup, image=photo, bg="white")
        label_img.image = photo
        label_img.pack(pady=10)
    else:
        CTkLabel(popup, text="Pas d'image disponible").pack(pady=10)

    # Gestion des actions utilisateur
    action_frame = CTkFrame(popup, fg_color="transparent")
    action_frame.pack(pady=10)

    def modifier_produit():
        """Affiche une interface permettant de modifier les informations du produit et de les enregistrer via Airtable."""
        for widget in popup.winfo_children():
            widget.destroy()

        popup.title(f"Modifier {product['nom']}")

        categories = ["BUSE", "CALE", "CHEVILLE", "CLIENT", "COFFRET", "CONSOMMABLE", "DISQUE", "ELECTRICITE", "EMBOUT", "ENTREE D AIR",
                    "FÊNETRE", "FORET", "HABILLAGE", "LAMES", "MACHINE", "MOUSSE PU", "NETTOYAGE", "PROTECTION", "NON STOCKÉ", "OUTILLAGE A MAIN", 
                    "POIGNÉE", "SCELLEMENT CHIMIQUE", "SCOTCH", "SECURITE", "SILICONE", "SPÉCIAL", "TELECOMMANDE", "VÉHICULES", "VETEMENT", "VISSERIE", "VMC", 
                    "VOLET BATTANT", "VOLET ROULANT", "MOTEUR"]

        fournisseurs = ["AMAZON", "BERNER", "BIPA", "BRICOZOR", "BUBENDORFF", "COGEFERM", "COPRODEX", "EUROMATIK", "FORUM DU BATIMENT",
                            "FOUSSIER", "FRANCIAFLEX", "ILLBRUCK", "KLINE", "KLOSE BESSER", "LARIVIERE", "LEGRAND", "LEROY MERLIN", "MANO MANO",
                            "PREFAL", "RABONI", "RECA", "SOMFY", "VALENTE", "SONEPAR", "WURTH"]

        CTkLabel(popup, text="Modifier le produit", font=("Arial Bold", 16)).pack(pady=10)

        # Champs de saisie
        fields = {
            "Nom": product["nom"],
            "Référence": product["ref"],
            "Fournisseur": product["fournisseur"],
            "Catégorie": product["categorie"],
            "Minimum": str(product["mini"]),
            "Maximum": str(product["max"]),
            "Prix": str(product["prix"]) if "prix" in product else "",
        }

        entries = {}

        for label, value in fields.items():
            frame = CTkFrame(popup, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)

            CTkLabel(frame, text=label + ":", width=15).pack(side="left", padx=10)

            # Utilisation d'une liste déroulante pour Catégorie et Fournisseur
            if label == "Catégorie":
                entry = CTkComboBox(frame, values=categories)
                entry.set(value)  # Définir la valeur actuelle
            elif label == "Fournisseur":
                entry = CTkComboBox(frame, values=fournisseurs)
                entry.set(value)  # Définir la valeur actuelle
            else:
                entry = CTkEntry(frame)
                entry.insert(0, value)

            entry.pack(side="right", fill="x", expand=True)
            entries[label] = entry

        # Bouton de sauvegarde
        def sauvegarder_modifications():
            """Enregistre les modifications du produit via l'API Airtable."""
            try:
                updated_data = {
                    "Nom": entries["Nom"].get(),
                    "Référence": entries["Référence"].get(),
                    "Catégorie": entries["Catégorie"].get(),
                    "Fournisseur": entries["Fournisseur"].get(),
                    "Minimum": int(entries["Minimum"].get()),
                    "Maximum": int(entries["Maximum"].get()),
                    "Prix Unitaire": float(entries["Prix"].get()) if entries["Prix"].get() else None,
                }

                # Appel de la fonction pour mettre à jour dans Airtable
                sucess = update_product(product["id"], updated_data)
                reset_filters()
                if sucess is not None:
                    print("✅ Requête envoyée avec succès !")

                    # Mise à jour locale
                    if product["id"] in scanned_products:
                        scanned_products[product["id"]].update(updated_data)

                    CTkMessagebox(title="Succès", message="Modifications enregistrées.", icon="info")
                    popup.withdraw()
                else:
                    print("❌ Mise à jour échouée, annulation de la mise à jour locale.")
                    CTkMessagebox(title="Erreur", message="Échec de la mise à jour dans Airtable.", icon="warning")

            except ValueError as e:
                print(f"❌ Erreur de conversion : {e}")
                CTkMessagebox(title="Erreur", message="Veuillez entrer des valeurs valides.", icon="warning")

            except Exception as e:
                print(f"❌ Erreur inattendue : {e}")
                CTkMessagebox(title="Erreur", message=f"Échec de la mise à jour : {e}", icon="warning")

        CTkButton(popup, text="Sauvegarder", fg_color="green", command=sauvegarder_modifications).pack(pady=10)
        CTkButton(popup, text="Annuler", fg_color="red", command=popup.withdraw).pack()

    def confirm_entry_exit(entry, exit, reference, quantity):
        """Action de confirmation pour l'entrée/sortie."""
        if not reference or not quantity:
            CTkMessagebox(title="Erreur", message="Référence et quantité requises.", icon="warning")
            return

        try:
            quantity_value = int(quantity)
            if exit:
                quantity_value = -abs(quantity_value)
        except ValueError:
            CTkMessagebox(title="Erreur", message="Quantité invalide. Veuillez entrer un nombre entier.", icon="error")
            return

        print(f"Traitement de l'action: {'Entrée' if entry else 'Sortie'} - Réf: {reference}, Qté: {quantity_value}")

        loading_label = CTkLabel(action_frame, text="Chargement...")
        loading_label.pack(pady=5)
        progress_bar = CTkProgressBar(action_frame, mode="determinate")
        progress_bar.pack(pady=5)
        progress_bar.start()
        popup.update()

        action = "Ajouter" if entry else "Réduire" if exit else "Aucune sélection"
        if action != "Aucune sélection":
            try:
                mov_prod(product["id"], action, reference, quantity_value, "username")
                new_quantity = scanned_products[product["id"]]["qte"] + quantity_value
                update_product_quantity(product["id"], new_quantity)
                CTkMessagebox(title="Succès", message="Mise à jour réussie!", icon="info")
                progress_bar.destroy()
                loading_label.destroy()
                reset_action_frame()
            except Exception as e:
                progress_bar.destroy()
                loading_label.destroy()
                CTkMessagebox(title="Erreur", message=f"Erreur: {e}", icon="error")
        else:
            progress_bar.destroy()
            loading_label.destroy()

    def show_entry_exit():
        for widget in action_frame.winfo_children():
            widget.destroy()

        entry_var, exit_var = BooleanVar(), BooleanVar()
        grid_frame = CTkFrame(action_frame, fg_color="transparent")
        grid_frame.pack()

        labels = ["Entrée", "Sortie", "Référence", "Quantité"]
        for idx, text in enumerate(labels):
            CTkLabel(grid_frame, text=text).grid(row=0, column=idx, padx=5, pady=5)

        widgets = [
            CTkCheckBox(grid_frame, variable=entry_var, text=""),
            CTkCheckBox(grid_frame, variable=exit_var, text=""),
            CTkEntry(grid_frame),
            CTkEntry(grid_frame)
        ]

        for idx, widget in enumerate(widgets):
            widget.grid(row=1, column=idx, padx=5, pady=5)

        button_frame = CTkFrame(action_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        CTkButton(button_frame, text="Confirmer", fg_color="black",
                  command=lambda: confirm_entry_exit(
                      entry_var.get(), exit_var.get(), widgets[2].get(), widgets[3].get()
                  )).grid(row=0, column=0, padx=10)
        CTkButton(button_frame, text="Retour", fg_color="black", command=reset_action_frame).grid(row=0, column=1, padx=10)

    def reset_action_frame():
        for widget in action_frame.winfo_children():
            widget.destroy()

        buttons = [
            ("Modifier", modifier_produit),
            ("Entrée/Sortie", show_entry_exit),
            ("Fermer", popup.withdraw)
        ]

        for text, cmd in buttons:
            CTkButton(action_frame, text=text, fg_color="black", command=cmd).pack(pady=5)

    reset_action_frame()
