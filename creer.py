from customtkinter import *
import tkinter
from fonction import cree_prod

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"

def show_creer(main_view):
    """Affiche l'interface de création de produit."""
    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    # Conteneur principal
    main_view.configure(bg_color=BG_COLOR)
    
    # Titre
    CTkLabel(master=main_view, text="Création de Produit", font=("Arial Black", 25), text_color="white").pack(anchor="nw", pady=(20, 10), padx=27)

    # Conteneur des champs
    fields_frame = CTkFrame(master=main_view, fg_color="#4b5e61", corner_radius=15)
    fields_frame.pack(fill="both", padx=27, pady=20)

    # Champs pour le nom du produit
    CTkLabel(master=fields_frame, text="Nom du Produit", font=("Arial Bold", 17), text_color="white").pack(anchor="nw", pady=(15, 0), padx=27)
    nom_entry = CTkEntry(master=fields_frame, fg_color="white", text_color=TEXT_COLOR, corner_radius=8)
    nom_entry.pack(fill="x", pady=(5, 10), padx=27)

    # Champs pour la référence produit
    CTkLabel(master=fields_frame, text="Référence Produit", font=("Arial Bold", 17), text_color="white").pack(anchor="nw", pady=(10, 0), padx=27)
    ref_entry = CTkEntry(master=fields_frame, fg_color="white", text_color=TEXT_COLOR, corner_radius=8)
    ref_entry.pack(fill="x", pady=(5, 10), padx=27)

    # Menu déroulant pour la catégorie
    CTkLabel(master=fields_frame, text="Catégorie", font=("Arial Bold", 17), text_color="white").pack(anchor="nw", pady=(10, 0), padx=27)
    category_menu = CTkOptionMenu(master=fields_frame, values=["SILICONE", "Maison", "Vêtements", "Alimentation"], fg_color="white", text_color=TEXT_COLOR, corner_radius=8)
    category_menu.pack(fill="x", pady=(5, 10), padx=27)

    # Menu déroulant pour le fournisseur
    CTkLabel(master=fields_frame, text="Fournisseur", font=("Arial Bold", 17), text_color="white").pack(anchor="nw", pady=(10, 0), padx=27)
    supplier_menu = CTkOptionMenu(master=fields_frame, values=["WURTH", "Fournisseur B", "Fournisseur C"], fg_color="white", text_color=TEXT_COLOR, corner_radius=8)
    supplier_menu.pack(fill="x", pady=(5, 10), padx=27)

    # Gestion de la quantité avec les boutons + et -
    CTkLabel(master=fields_frame, text="Quantité", font=("Arial Bold", 17), text_color="white").pack(anchor="nw", pady=(10, 0), padx=27)
    quantity_frame = CTkFrame(master=fields_frame, fg_color="transparent")
    quantity_frame.pack(fill="x", pady=(5, 10), padx=27)

    quantity_var = tkinter.IntVar(value=1)  # Quantité initiale
    def increase_quantity(): quantity_var.set(quantity_var.get() + 1)
    def decrease_quantity(): 
        if quantity_var.get() > 0: quantity_var.set(quantity_var.get() - 1)

    CTkButton(master=quantity_frame, text="-", width=40, command=decrease_quantity, fg_color=HIGHLIGHT_COLOR, hover_color="#207244").pack(side="left", padx=(0, 10))
    CTkLabel(master=quantity_frame, textvariable=quantity_var, font=("Arial Bold", 16), text_color="white").pack(side="left", padx=(0, 10))
    CTkButton(master=quantity_frame, text="+", width=40, command=increase_quantity, fg_color=HIGHLIGHT_COLOR, hover_color="#207244").pack(side="left")

    # Champs pour le prix
    CTkLabel(master=fields_frame, text="Prix", font=("Arial Bold", 17), text_color="white").pack(anchor="nw", pady=(10, 0), padx=27)
    price_entry = CTkEntry(master=fields_frame, fg_color="white", text_color=TEXT_COLOR, corner_radius=8)
    price_entry.pack(fill="x", pady=(5, 10), padx=27)

    # Bouton "Créer"
    def handle_create():
        """Récupère les valeurs saisies et appelle la fonction cree_prod."""
        nom = nom_entry.get()
        ref = ref_entry.get()
        categorie = category_menu.get()
        fournisseur = supplier_menu.get()
        quantite = quantity_var.get()
        prix = price_entry.get()

        try:
            prix = float(prix)  # Convertir le prix en float
        except ValueError:
            print("Erreur : Le prix doit être un nombre valide.")
            return

        # Appel de la fonction cree_prod
        cree_prod(nom, ref, categorie, fournisseur, quantite, prix)
        if cree_prod:
            label_status.configure(text=f"Produit : {nom} créé")



        # Réinitialisation des champs après la création
        nom_entry.delete(0, tkinter.END)
        ref_entry.delete(0, tkinter.END)
        category_menu.set("SILICONE")
        supplier_menu.set("WURTH")
        quantity_var.set(1)
        price_entry.delete(0, tkinter.END)

    CTkButton(master=main_view, text="Créer", font=("Arial Bold", 17), command=handle_create, fg_color=HIGHLIGHT_COLOR, text_color="white", hover_color="#207244").pack(side="right", pady=(20, 10), padx=27)

    label_status = CTkLabel(master=main_view, text="", font=("Arial", 24, "bold"), text_color="#00ff27", fg_color="transparent")
    label_status.pack(pady=(5, 15))

    label_status.configure(text="")
