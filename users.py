from customtkinter import *
from fonction import load_users_from_json
from tkinter import messagebox
from PIL import Image, ImageTk

def show_users(main_view):
    """Affiche la page des utilisateurs dans la vue principale."""
    # Efface tout le contenu existant dans la vue principale
    for widget in main_view.winfo_children():
        widget.destroy()

    # Couleurs
    BG_COLOR = "#f8f9fa"
    HEADER_COLOR = "#2A8C55"
    ROW_COLOR_1 = "#e8f5e9"
    ROW_COLOR_2 = "#ffffff"
    TEXT_COLOR = "#495057"

    # Conteneur principal
    users_frame = CTkFrame(master=main_view, fg_color=BG_COLOR, corner_radius=20)
    users_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Titre avec bouton de rafraîchissement
    title_frame = CTkFrame(master=users_frame, fg_color="transparent")
    title_frame.pack(fill="x", padx=20, pady=(20, 10))

    title_label = CTkLabel(
        master=title_frame,
        text="Liste des utilisateurs",
        font=("Arial Bold", 24),
        text_color=HEADER_COLOR,
        anchor="w"
    )
    title_label.pack(side="left", padx=10)

    refresh_icon = CTkImage(Image.open("icons/refresh.png"), size=(20, 20))
    refresh_button = CTkButton(
        master=title_frame,
        image=refresh_icon,
        text="Rafraîchir",
        font=("Arial", 14),
        fg_color="#d9e7d8",
        text_color=HEADER_COLOR,
        hover_color="#c8d8c7",
        corner_radius=15,
        command=lambda: show_users(main_view)
    )
    refresh_button.pack(side="right", padx=10)

    # Barre de recherche
    search_frame = CTkFrame(master=users_frame, fg_color="transparent")
    search_frame.pack(fill="x", padx=20, pady=(0, 10))

    search_label = CTkLabel(
        master=search_frame,
        text="Rechercher :",
        font=("Arial", 14),
        text_color=TEXT_COLOR
    )
    search_label.pack(side="left", padx=10)

    search_var = StringVar()

    search_entry = CTkEntry(
        master=search_frame,
        textvariable=search_var,
        placeholder_text="Tapez un nom...",
        font=("Arial", 14),
        corner_radius=15,
        width=300
    )
    search_entry.pack(side="left", padx=10)

    # Fonction de recherche
    def filter_users():
        filtered_users = {k: v for k, v in users.items() if search_var.get().lower() in v["nom"].lower()}
        populate_table(filtered_users)

    search_button = CTkButton(
        master=search_frame,
        text="Rechercher",
        font=("Arial", 14),
        fg_color=HEADER_COLOR,
        text_color="white",
        hover_color="#1e6e3b",
        corner_radius=15,
        command=filter_users
    )
    search_button.pack(side="left", padx=10)

    # Chargement des utilisateurs
    users = load_users_from_json("users.json")
    if not users:
        messagebox.showerror("Erreur", "Impossible de charger les utilisateurs.")
        return

    # Tableau
    table_frame = CTkFrame(master=users_frame, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # En-têtes du tableau
    headers = ["ID Utilisateur", "Nom", "Rôle", "Société"]
    for col, header in enumerate(headers):
        header_label = CTkLabel(
            master=table_frame,
            text=header,
            font=("Arial Bold", 14),
            text_color=HEADER_COLOR,
            anchor="w"
        )
        header_label.grid(row=0, column=col, padx=10, pady=5, sticky="w")

    # Fonction pour remplir le tableau
    def populate_table(data):
        # Vider le tableau avant de remplir avec les nouvelles données
        for widget in table_frame.winfo_children():
            if isinstance(widget, CTkLabel) and widget != title_label:
                widget.destroy()

        # Remplir le tableau avec les utilisateurs
        for row, (user_id, user_data) in enumerate(data.items(), start=1):
            bg_color = ROW_COLOR_1 if row % 2 == 0 else ROW_COLOR_2

            id_label = CTkLabel(
                master=table_frame,
                text=user_id,
                font=("Arial", 12),
                text_color=TEXT_COLOR,
                fg_color=bg_color,
                corner_radius=10
            )
            id_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

            name_label = CTkLabel(
                master=table_frame,
                text=user_data["nom"],
                font=("Arial", 12),
                text_color=TEXT_COLOR,
                fg_color=bg_color,
                corner_radius=10
            )
            name_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")

            role_label = CTkLabel(
                master=table_frame,
                text=user_data["role"],
                font=("Arial", 12),
                text_color=TEXT_COLOR,
                fg_color=bg_color,
                corner_radius=10
            )
            role_label.grid(row=row, column=2, padx=10, pady=5, sticky="w")

            company_label = CTkLabel(
                master=table_frame,
                text=user_data["societe"],
                font=("Arial", 12),
                text_color=TEXT_COLOR,
                fg_color=bg_color,
                corner_radius=10
            )
            company_label.grid(row=row, column=3, padx=10, pady=5, sticky="w")

    # Appeler une première fois avec tous les utilisateurs
    populate_table(users)
