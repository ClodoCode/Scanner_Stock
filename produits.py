from customtkinter import *
import requests
from tkinter import Canvas
from PIL import Image, ImageTk
from fonction import get_produit_info

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
    product_canvas.create_text(250, 150, text="Scannez un produit pour voir les détails.", 
                                font=("Arial", 16), fill="gray", tags="placeholder")


def handle_scan_prod(scanned_code):
    """
    Gère le scan du produit et affiche ses détails sur le Canvas.
    """
    global product_canvas

    # Nettoyage du code scanné
    scanned_code = scanned_code.strip()

    # Récupérer les informations du produit via `get_produit_info`
    product_info = get_produit_info(scanned_code)

    # Nettoyer le canvas pour préparer l'affichage des détails
    product_canvas.delete("all")

    if product_info:
        # Charger l'image du produit
        if product_info["photo"]:
            try:
                # Charger l'image à partir de l'URL
                image = Image.open(requests.get(product_info["photo"], stream=True).raw)
                image = image.resize((150, 150), Image.ANTIALIAS)
                product_image = ImageTk.PhotoImage(image)
                product_canvas.image = product_image  # Empêche le garbage collection
                product_canvas.create_image(250, 100, image=product_image)
            except Exception as e:
                print(f"Erreur lors du chargement de l'image : {e}")
                product_canvas.create_text(250, 100, text="Image non disponible", font=("Arial", 14), fill="gray")
        else:
            product_canvas.create_text(250, 100, text="Aucune image disponible", font=("Arial", 14), fill="gray")

        # Afficher les détails du produit
        product_canvas.create_text(250, 200, text=f"Nom : {product_info['nom']}", font=("Arial Bold", 16), fill="#2A8C55")
        product_canvas.create_text(250, 240, text=f"Fournisseur : {product_info['fournisseur']}", font=("Arial", 14), fill="black")
        product_canvas.create_text(250, 280, text=f"Quantité : {product_info['qte']}", font=("Arial", 14), fill="black")
        product_canvas.create_text(250, 320, text=f"Catégorie : {product_info['categorie']}", font=("Arial", 14), fill="black")
    else:
        # Afficher un message d'erreur si le produit est introuvable
        product_canvas.create_text(250, 150, text="Produit introuvable.", font=("Arial Bold", 16), fill="red")
