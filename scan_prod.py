from customtkinter import *
from tkinter import Canvas
from produits import list_produit_rea

def show_scan_prod(main_view):
    """Affiche un tableau de bord moderne avec structure ajustée et design enrichi."""
    # Effacer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()
