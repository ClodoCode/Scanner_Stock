from tkinter import *
from customtkinter import *
from functools import partial  # Pour utiliser partial
from fonction import list_command, plus_list_prod, moins_list_prod

# Couleurs modernes
BG_COLOR = "#4b5e61"
HEADER_BG = "#2A8C55"
TEXT_COLOR = "#333333"
HIGHLIGHT_COLOR = "#2A8C55"


# Dictionnaires pour suivre les produits scannés et leurs images
scanned_products = {}

def show_commande(main_view):

    # Effacer les widgets existants dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    command = list_command()

    print(f"{command}")