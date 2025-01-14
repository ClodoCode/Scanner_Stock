from customtkinter import *
from PIL import Image, ImageTk

def show_dashboard(main_view):
    """Affiche une interface similaire au tableau de bord fourni."""
    # Effacer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()

    # Couleurs principales
    bg_color = "#F7F8FA"
    text_color = "#333333"
    box_bg_color = "white"
    accent_color = "#2A8C55"

    # Configuration générale
    main_view.configure(fg_color="#ebf2f3")

     # Titre de la section
    title_label = CTkLabel(
        main_view,
        text="Veuillez scannez un code barre",
        font=("Arial", 35, "bold"),
        text_color="red",
        anchor="center",
    )
    title_label.pack(pady=(10, 5))

    # Section "Sales Activity"
    sales_frame = CTkFrame(master=main_view, fg_color=box_bg_color, corner_radius=10)
    sales_frame.place(relx=0.05, rely=0.1, relwidth=0.9, relheight=0.25)

    CTkLabel(master=sales_frame, text="Sales Activity", font=("Helvetica", 16, "bold"), text_color=text_color).place(relx=0.02, rely=0.05)

    # Boîtes pour "Sales Activity"
    sales_data = [
        {"label": "TO BE PACKED", "value": "55", "color": "#0078D4"},
        {"label": "TO BE SHIPPED", "value": "3", "color": "#F7630C"},
        {"label": "TO BE DELIVERED", "value": "4", "color": "#2D89EF"},
        {"label": "TO BE INVOICED", "value": "79", "color": "#FFB900"},
    ]

    for i, data in enumerate(sales_data):
        box = CTkFrame(master=sales_frame, fg_color=box_bg_color, corner_radius=10, border_width=1, border_color="#D0D0D0")
        box.place(relx=0.02 + (0.24 * i), rely=0.3, relwidth=0.22, relheight=0.6)

        CTkLabel(master=box, text=data["value"], font=("Helvetica", 24, "bold"), text_color=data["color"]).place(relx=0.5, rely=0.3, anchor="center")
        CTkLabel(master=box, text=data["label"], font=("Helvetica", 12), text_color=text_color).place(relx=0.5, rely=0.7, anchor="center")

    # Section "Inventory Summary"
    inventory_frame = CTkFrame(master=main_view, fg_color=box_bg_color, corner_radius=10)
    inventory_frame.place(relx=0.05, rely=0.4, relwidth=0.4, relheight=0.2)

    CTkLabel(master=inventory_frame, text="Inventaire", font=("Helvetica", 22, "bold"), text_color=text_color).place(relx=0.05, rely=0.1)

    inventory_data = [
        {"label": "Quantité total d'item", "value": "463"},
        {"label": "Quantité à recevoir", "value": "161"},
    ]

    for i, data in enumerate(inventory_data):
        CTkLabel(master=inventory_frame, text=data["label"], font=("Helvetica", 22), text_color=text_color).place(relx=0.05, rely=0.35 + i * 0.3)
        CTkLabel(master=inventory_frame, text=data["value"], font=("Helvetica", 20, "bold"), text_color=accent_color).place(relx=0.7, rely=0.35 + i * 0.3)

    # Section "Product Details"
    product_frame = CTkFrame(master=main_view, fg_color=box_bg_color, corner_radius=10)
    product_frame.place(relx=0.5, rely=0.4, relwidth=0.45, relheight=0.2)

    CTkLabel(master=product_frame, text="Product Details", font=("Helvetica", 22, "bold"), text_color=text_color).place(relx=0.05, rely=0.1)

    CTkLabel(master=product_frame, text="Produits en quantité faible", font=("Helvetica", 20), text_color="#E81123").place(relx=0.05, rely=0.4)
    CTkLabel(master=product_frame, text="3", font=("Helvetica", 20, "bold"), text_color=text_color).place(relx=0.4, rely=0.4)

    CTkLabel(master=product_frame, text="Produit utilisé", font=("Helvetica", 20), text_color=text_color).place(relx=0.05, rely=0.7)
    CTkLabel(master=product_frame, text="89%", font=("Helvetica", 20, "bold"), text_color=accent_color).place(relx=0.4, rely=0.7)

    # Section "Top Selling Items" (simplifiée)
    selling_frame = CTkFrame(master=main_view, fg_color=box_bg_color, corner_radius=10)
    selling_frame.place(relx=0.05, rely=0.65, relwidth=0.9, relheight=0.2)

    CTkLabel(master=selling_frame, text="Top Selling Items", font=("Helvetica", 22, "bold"), text_color=text_color).place(relx=0.05, rely=0.1)

    # Simuler des éléments de vente
    items = ["Orange Jacket", "Blue Romper", "Pink Pants"]
    for i, item in enumerate(items):
        CTkLabel(master=selling_frame, text=f"{item}", font=("Helvetica", 22), text_color=text_color).place(relx=0.05 + i * 0.3, rely=0.4)
        CTkLabel(master=selling_frame, text=f"{10 * (i + 1)} pcs", font=("Helvetica", 14, "bold"), text_color=accent_color).place(relx=0.05 + i * 0.3, rely=0.7)