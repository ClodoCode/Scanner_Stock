from customtkinter import *
import requests
from tkinter import Canvas
from PIL import Image, ImageTk
from fonction import get_produit_info

# Dictionnaires pour suivre les produits scannés et les images associées
scanned_products = {}
product_images = {}

def show_scan_prod(main_view):
    """
    Affiche la vue de scan des produits dans la zone principale.
    """
    # Effacer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()

    # Titre de la page
    title_label = CTkLabel(master=main_view, text="Scan des Produits", font=("Arial Bold", 24), text_color="#2A8C55")
    title_label.pack(pady=(20, 10))

    # Créer un Canvas pour afficher les produits
    global product_canvas
    product_canvas = Canvas(main_view, bg="#F5F5F5", highlightthickness=0)
    product_canvas.pack(fill="both", expand=True, padx=20, pady=20)

    # Ajouter un texte temporaire indiquant d'attendre un scan
    #product_canvas.create_text(250, 150, text="Scannez un produit pour voir les détails.", font=("Arial", 16), fill="gray", tags="placeholder")


def handle_scan_prod(scanned_code):
    """
    Gère le scan du produit et affiche ses détails sur le Canvas.
    """
    global product_canvas, scanned_products, product_images

    # Nettoyage du code scanné
    scanned_code = scanned_code.strip()

    # Vérifie si le produit a déjà été scanné
    if scanned_code in scanned_products:
        print(f"Le produit avec le code {scanned_code} est déjà affiché.")
        return

    # Récupérer les informations du produit via `get_produit_info`
    product_info = get_produit_info(scanned_code)

    if product_info:
        # Ajouter le produit au dictionnaire des produits scannés
        scanned_products[scanned_code] = product_info

        # Calcul de la position (colonne et ligne) pour afficher le produit
        num_products = len(scanned_products)
        row = (num_products - 1) // 3  # Maximum 3 colonnes
        col = (num_products - 1) % 3   # Maximum 4 produits par ligne
        x_offset = 20 + col * 500      # Espacement horizontal (300 pixels entre colonnes)
        y_offset = 20 + row * 250      # Espacement vertical (250 pixels entre lignes)

        # Charger l'image du produit
        if product_info["photo"]:
            try:
                # Charger l'image à partir de l'URL
                image = Image.open(requests.get(product_info["photo"], stream=True).raw)
                image = image.resize((150, 180), Image.Resampling.LANCZOS)
                product_image = ImageTk.PhotoImage(image)
                product_images[scanned_code] = product_image  # Stocker l'image pour éviter le garbage collection
                product_canvas.create_image(x_offset + 75, y_offset + 75, image=product_image)
            except Exception as e:
                print(f"Erreur lors du chargement de l'image : {e}")
                product_canvas.create_text(x_offset + 75, y_offset + 75, text="Image non disponible", font=("Arial", 14), fill="gray")
        else:
            product_canvas.create_text(x_offset + 75, y_offset + 75, text="Aucune image disponible", font=("Arial", 14), fill="gray")

        # Afficher les détails du produit
        product_canvas.create_text(x_offset + 180, y_offset + 30, text=f"Nom : {product_info['nom']}", font=("Arial Bold", 14), fill="#2A8C55", anchor="w")
        product_canvas.create_text(x_offset + 180, y_offset + 70, text=f"Fournisseur : {product_info['fournisseur']}", font=("Arial", 12), fill="black", anchor="w")
        product_canvas.create_text(x_offset + 180, y_offset + 110, text=f"Quantité : {product_info['qte']}", font=("Arial", 12), fill="black", anchor="w")
        product_canvas.create_text(x_offset + 180, y_offset + 150, text=f"Catégorie : {product_info['categorie']}", font=("Arial", 12), fill="black", anchor="w")
    else:
        # Afficher un message d'erreur si le produit est introuvable
        product_canvas.create_text(250, 150, text="Produit introuvable.", font=("Arial Bold", 16), fill="red")
