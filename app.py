from customtkinter import *
import tkinter as tk
import json
from PIL import Image, ImageTk
from dashboard import show_dashboard
from sortie import show_sortie, handle_scan_reduire, get_produits_scannes_r
from entree import show_entree, handle_scan_entree, get_produits_scannes_a
from fonction import load_users_from_json
from produits import envoie_msg_franck

class Application(CTk):
    def __init__(self):
        super().__init__()

        # Initialisation des variables
        self.user_identified = None
        self.current_user_name = ""
        self.current_user_role = ""  # Variable pour stocker le rôle de l'utilisateur
        self.scan_code = ""
        self.authorized_users = load_users_from_json("users.json")
        self.current_tab = ""  # Initialisation de current_tab
        self.produits_scannes_r = get_produits_scannes_r()
        self.produits_scannes_a = get_produits_scannes_a()

        # Configuration de l'interface
        self.configure_window()
        self.create_sidebar()
        self.create_main_view()
        self.update_tab_access()  # Désactiver les onglets au démarrage

        # Lier les événements de pression de touche à la fonction
        self.bind("<Key>", self.capture_keypress)

    def get_current_user_name(self):
        return self.current_user_name

    def configure_window(self):
        """Configurer la fenêtre principale de l'application."""
        screen_width = self.winfo_screenwidth()  # Largeur de l'écran
        screen_height = self.winfo_screenheight()  # Hauteur de l'écran

        # Définir la géométrie de la fenêtre avec la taille de l'écran
        self.geometry(f"{screen_width}x{screen_height}")  # Taille de la fenêtre égale à l'écran

        # Maximiser la fenêtre
        self.state('zoomed')

        # Centrer la fenêtre
        position_top = int((screen_height - self.winfo_height()) / 2)
        position_left = int((screen_width - self.winfo_width()) / 2)
        self.geometry(f"+{position_left}+{position_top}")

        # Définir le titre de la fenêtre
        self.title("Logiciel Stock")  # Change le nom dans la barre de titre

        # Définir l'icône de la fenêtre
        self.iconbitmap("logo.ico")  # Remplacer par le chemin vers ton icône .ico

        # Autres configurations
        self.resizable(True, True)
        set_appearance_mode("light")
        self.configure(bg="#2A8C55")


    def create_sidebar(self):
        """Créer la barre latérale avec ses éléments."""
        self.sidebar_frame = CTkFrame(master=self, fg_color="#4b5e61", width=176, height=650, corner_radius=0)
        self.sidebar_frame.pack_propagate(0)
        self.sidebar_frame.pack(fill="y", anchor="w", side="left")

        # Logo
        logo_img_data = Image.open("logo.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(77.68, 85.42))
        CTkLabel(master=self.sidebar_frame, text="", image=logo_img).pack(pady=(38, 68), anchor="center")

        # Boutons
        self.dashboard_button = self.create_button(self.sidebar_frame, "Dashboard", "package_icon.png", lambda: show_dashboard(self.main_view))
        self.reduire_button = self.create_button(self.sidebar_frame, "Sortie", "logistics_icon.png", lambda: show_sortie(self.main_view))
        self.ajouter_button = self.create_button(self.sidebar_frame, "Entrée", "delivered_icon.png", lambda: show_entree(self.main_view))

        # Statut de la connexion
        self.label_sidebar_status = CTkLabel(master=self.sidebar_frame, text="Déconnecté", fg_color="transparent", text_color="red", font=("Arial Bold", 14), anchor="w")
        self.label_sidebar_status.pack(anchor="center", ipady=5, pady=(582, 0))

        # Label pour afficher le rôle sous le nom de l'utilisateur
        self.label_sidebar_role = CTkLabel(master=self.sidebar_frame, text="", fg_color="transparent", text_color="black", font=("Arial", 12), anchor="w")
        self.label_sidebar_role.pack(anchor="center", ipady=5, pady=(0, 10))  # Espacement sous le nom de l'utilisateur

    def create_button(self, parent, text, img_path, command):
        """Créer un bouton dans la barre latérale."""
        img_data = Image.open(img_path)
        img = CTkImage(dark_image=img_data, light_image=img_data)
        button = CTkButton(master=parent, image=img, text=text, fg_color="#fff", font=("Arial Bold", 14), text_color="#2A8C55", hover_color="#eee", command=command, anchor="w")
        button.pack(anchor="center", ipady=5, pady=(16, 0))
        return button

    def create_main_view(self):
        """Créer la vue principale de l'application."""
        self.main_view = CTkFrame(master=self, fg_color="#fff", corner_radius=0)
        self.main_view.pack_propagate(0)
        self.main_view.pack(side="right", fill="both", expand=True)

        # Afficher le dashboard au démarrage
        self.after(100, lambda: show_dashboard(self.main_view))

    def update_sidebar_status(self):
        """Met à jour le statut de la barre latérale (connecté ou déconnecté)."""
        if self.user_identified is None:
            self.label_sidebar_status.configure(text="Déconnecté", text_color="red")
            self.label_sidebar_role.configure(text="")  # Supprimer le rôle si non connecté
        else:
            self.label_sidebar_status.configure(text=f"{self.current_user_name}", text_color="black")
            self.label_sidebar_role.configure(text=f"Rôle : {self.current_user_role}", text_color="black")  # Afficher le rôle

    def update_tab_access(self):
        """Met à jour l'accès aux onglets en fonction de l'utilisateur."""
        if self.user_identified is None:
            self.reduire_button.configure(state="disabled")
            self.ajouter_button.configure(state="disabled")
        else:
            user_role = self.authorized_users[self.user_identified]["role"]
            self.current_user_role = user_role  # Mettre à jour le rôle de l'utilisateur
            if user_role == "administrateur":
                self.reduire_button.configure(state="normal")
                self.ajouter_button.configure(state="normal")
            else:
                self.reduire_button.configure(state="normal")
                self.ajouter_button.configure(state="disabled")

    def logout(self):
        """Déconnecte l'utilisateur et réinitialise l'interface."""
        self.user_identified = None
        self.current_user_name = ""
        self.update_sidebar_status()
        self.update_tab_access()
        show_dashboard(self.main_view)
        print("Utilisateur déconnecté.")


    def handle_barcode(self):
        """Gère le scan du code-barres et la navigation entre les onglets."""

        scanned_code = self.scan_code.strip()
        username = self.current_user_name
        print(f"Code scanné : {scanned_code}")

        if scanned_code == "LOGOUT":
            self.logout()
            self.scan_code = ""
            return

        if self.user_identified is None:
            if scanned_code in self.authorized_users:
                self.user_identified = scanned_code
                self.current_user_name = self.authorized_users[scanned_code]["nom"]
                self.current_user_role = self.authorized_users[scanned_code]["role"]  # Récupérer le rôle
                self.update_sidebar_status()
                self.update_tab_access()
            else:
                self.label_sidebar_status.configure(text="Accès refusé", text_color="red")
            self.scan_code = ""
            return

        # Vérification si un onglet est déjà ouvert
        if self.current_tab == "sortie":
            handle_scan_reduire(scanned_code, username)
            if len(self.produits_scannes_r) > 0:
                return

        # Vérification si un onglet est déjà ouvert
        if self.current_tab == "entree":
            handle_scan_entree(scanned_code, username)
            if len(self.produits_scannes_a) > 0:
                return

        # Vérification de l'onglet actuel
        if scanned_code == "ACC001":
            self.current_tab = "dashboard"
            show_dashboard(self.main_view)
        elif scanned_code == "RED001":
            self.current_tab = "sortie"
            show_sortie(self.main_view)
        elif scanned_code == "AJT001":
            self.current_tab = "entree"
            show_entree(self.main_view)

    def capture_keypress(self, event):
        """Capture les frappes clavier et gère les codes-barres."""
        key = event.char
        if key.isalnum():
            self.scan_code += key
        elif key == "\r":  # Entrée : code complet
            self.handle_barcode()
            self.scan_code = ""  # Réinitialiser après traitement


# Exécution de l'application
if __name__ == "__main__":
    app = Application()
    app.mainloop()
