from customtkinter import *
from tkinter import Canvas
from produits import list_produit_rea

def show_dashboard(main_view):
    """Affiche un tableau de bord moderne avec structure ajustée et design enrichi."""
    # Effacer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()

    # Couleurs
    bg_color = "#3E3E57"  # Couleur de fond principale (plus claire mais pas blanche)
    card_color = "#464C77"  # Fond des cartes principales (plus lumineux)
    shadow_color = "#383C5A"  # Couleur d'ombre simulée pour les reliefs (plus claire)
    highlight_color = "#4B4F7C"  # Couleur lumineuse pour les bordures (plus douce)
    text_color = "#F1F1F6"  # Couleur du texte (clair mais pas blanc)
    accent_color = "#8A82FF"  # Couleur d'accent (plus douce)


    # Configuration générale
    main_view.configure(fg_color=bg_color)

    # Fonction pour créer un cadre avec relief
    def create_card(parent, x, y, width, height, title):
        shadow = CTkFrame(master=parent, fg_color=shadow_color, corner_radius=20)
        shadow.place(relx=x + 0.01, rely=y + 0.01, relwidth=width, relheight=height)

        card = CTkFrame(
            master=parent,
            fg_color=card_color,
            corner_radius=20,
            border_width=2,
            border_color=highlight_color,
        )
        card.place(relx=x, rely=y, relwidth=width, relheight=height)

        CTkLabel(
            master=card,
            text=title,
            font=("Arial", 24, "bold", "underline"),
            text_color=text_color,
        ).place(relx=0.05, rely=0.05)

        return card

    # Bloc long gauche (fusion des blocs 1 et 4)
    bloc_1 = create_card(main_view, 0.05, 0.05, 0.45, 0.85, "Produit à commander :")

    list_produit = list_produit_rea()
    if list_produit:
    # Organiser les produits par fournisseur
        produits_par_fournisseur = {}
        for produit in list_produit:
            fournisseur = produit['fournisseur']
            
            # Ajouter le produit dans la liste du fournisseur
            if fournisseur not in produits_par_fournisseur:
                produits_par_fournisseur[fournisseur] = []
            produits_par_fournisseur[fournisseur].append(produit)

        # Initialiser une variable pour l'offset vertical
        vertical_offset = 0.15  # Position verticale de départ
        
        # Afficher chaque fournisseur avec ses produits
        for fournisseur, produits in produits_par_fournisseur.items():
            # Afficher le nom du fournisseur
            CTkLabel(
                bloc_1,
                text=f"{fournisseur} :",
                font=("Arial", 16, "bold"),
                text_color=text_color
            ).place(relx=0.05, rely=vertical_offset)
            
            # Augmenter l'offset vertical pour le premier produit du fournisseur
            vertical_offset += 0.05
            
            # Afficher les produits sous ce fournisseur
            for produit in produits:
                CTkLabel(
                    bloc_1,
                    text=f"  {produit['nom']}",  # Ajouter un espace pour indenter le produit
                    font=("Arial", 14),
                    text_color=text_color
                ).place(relx=0.05, rely=vertical_offset)
                
                # Augmenter l'offset vertical pour le produit suivant
                vertical_offset += 0.05  # Augmenter pour qu'il apparaisse plus bas


    bloc_principal = create_card(main_view, 0.55, 0.05, 0.4, 0.55, "bloc_principal")

    # Ajouter des statistiques au bloc principal
    CTkLabel(bloc_principal, text="Revenu Aujourd'hui :", font=("Arial", 16), text_color=text_color).place(relx=0.05, rely=0.25)
    CTkLabel(bloc_principal, text="$62,970", font=("Arial", 24, "bold"), text_color=accent_color).place(relx=0.05, rely=0.35)

    CTkLabel(bloc_principal, text="Progression :", font=("Arial", 16), text_color=text_color).place(relx=0.05, rely=0.5)
    CTkProgressBar(bloc_principal, progress_color=accent_color).place(relx=0.05, rely=0.6, relwidth=0.9)


    # Bloc inférieur droit
    bloc_2 = create_card(main_view, 0.55, 0.65, 0.4, 0.25, "bloc_2")
