from customtkinter import *
import tkinter as tk
import json
import time
from PIL import Image, ImageTk
from dashboard import show_dashboard
from sortie import show_sortie, handle_scan_reduire, get_produits_scannes_r
from entree import show_entree, handle_scan_entree, get_produits_scannes_a
from fonction import load_users_from_json
from produits_v2 import show_all_products
from commande import show_commande
from users import show_users
from settings import show_settings

class Application(CTk):
    def __init__(self):
        super().__init__()

        # Initialisation des variables
        self.user_identified = None
        self.current_user_name = ""
        self.current_user_role = ""  # Variable pour stocker le rôle de l'utilisateur
        self.scan_code = ""
        self.authorized_users = load_users_from_json("users.json")
        self.current_tab = "dashboard"  # Initialisation de current_tab
        self.produits_scannes_r = get_produits_scannes_r()
        self.produits_scannes_a = get_produits_scannes_a()

        # Configuration de l'interface
        self.configure_window()
        self.create_sidebar()
        self.create_main_view()
        self.update_tab_access()  # Désactiver les onglets au démarrage

        # Variable pour vérifier si la fonction d'inactivité est en cours
        self.inactivity_timeout = 10  # Temps d'inactivité avant déconnexion (10 secondes pour les tests)

        # Lier les événements de pression de touche à la fonction
        self.bind("<Key>", self.capture_keypress)

        self.bind("<Configure>", self.on_resize)

    def configure_window(self):
        """Configurer la fenêtre principale de l'application."""
        # Configurer la fenêtre pour être redimensionnable
        self.geometry("1024x768")  # Taille par défaut
        self.resizable(True, True)  # Autoriser le redimensionnement
        self.state("zoomed")  # Maximiser la fenêtre au démarrage

        # Définir le titre et l'icône
        self.title("Logiciel Stock")
        self.iconbitmap("logo.ico")

        # Définir le mode d'apparence
        set_appearance_mode("light")
        self.configure(bg="#2A8C55")

    def on_resize(self, event):
        """Ajuster les éléments internes en fonction de la taille de la fenêtre."""
        # Ajuster la barre latérale pour qu'elle remplisse la hauteur
        self.sidebar_frame.configure(height=event.height)



    def create_sidebar(self):
        """Créer la barre latérale avec ses éléments."""
        self.sidebar_frame = CTkFrame(master=self, fg_color="#4b5e61", width=176, height=self.winfo_screenheight(), corner_radius=0)
        self.sidebar_frame.pack_propagate(0)
        self.sidebar_frame.pack(fill="y", anchor="w", side="left")

        # Logo
        logo_img_data = Image.open("logo.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(77.68, 85.42))
        CTkLabel(master=self.sidebar_frame, text="", image=logo_img).pack(pady=(38, 8), anchor="center")

        # Section 1 - Menu
        self.menu_section = CTkFrame(self.sidebar_frame, fg_color="transparent", corner_radius=10)
        self.menu_section.pack(fill="x", padx=25, pady=(16, 5))  # Padding pour espacer les sections
        
        # Texte "Menu"
        menu_label = CTkLabel(master=self.menu_section, text="Menu", font=("Arial", 16, "bold"), text_color="white", anchor="center")
        menu_label.pack(pady=(5, 5))

        # Boutons
        self.dashboard_button = self.create_button(self.sidebar_frame, "Dashboard", "package_icon.png", lambda: self.on_press_button("dash"))
        self.users_button = self.create_button(self.sidebar_frame, "Users", "group.png", lambda: self.on_press_button("users"))

        # Section 2 - Catégorie
        self.category_section = CTkFrame(self.sidebar_frame, fg_color="transparent", corner_radius=10)
        self.category_section.pack(fill="x", padx=16, pady=(16, 5))  # Padding pour espacer les sections
        
        # Texte "Catégorie"
        category_label = CTkLabel(master=self.category_section, text="Catégorie", font=("Arial", 16, "bold"), text_color="white", anchor="center")
        category_label.pack(pady=(5, 5))

        username = self.current_user_name

        self.reduire_button = self.create_button(self.sidebar_frame, "Sortie", "logistics_icon.png", lambda: self.on_press_button("sortie"))
        self.ajouter_button = self.create_button(self.sidebar_frame, "Entrée", "delivered_icon.png", lambda: self.on_press_button("entree"))
        self.produit_button = self.create_button(self.sidebar_frame, "Produits", "parcel.png", lambda: self.on_press_button("prod"))
        self.commande_button = self.create_button(self.sidebar_frame, "Commande", "tracking.png", lambda: self.on_press_button("command"))
        self.settings_button = self.create_button(self.sidebar_frame, "Settings", "gear.png", lambda: self.on_press_button("settings"))

        # Conteneur pour les éléments de statut et déconnexion
        self.footer_frame = CTkFrame(master=self.sidebar_frame, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", pady=10)  # Toujours en bas, avec un peu de marge

        # Statut de la connexion
        self.label_sidebar_status = CTkLabel(master=self.footer_frame,text="Déconnecté", fg_color="transparent", text_color="red", font=("Arial Bold", 16), anchor="w",)
        self.label_sidebar_status.pack(anchor="center", ipady=5, pady=(0, 5))

        # Label pour afficher le rôle sous le nom de l'utilisateur
        self.label_sidebar_role = CTkLabel(master=self.footer_frame,text="", fg_color="transparent", text_color="black", font=("Arial", 16), anchor="w",)
        self.label_sidebar_role.pack(anchor="center", ipady=5, pady=(0, 10))  # Espacement sous le nom

        # Bouton de déconnexion
        self.logout_button = self.create_button(self.footer_frame, "Déconnexion", "shutdown.png", lambda: self.logout())
        

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
            self.label_sidebar_status.configure(text=f"{self.current_user_name}", text_color="white")
            self.label_sidebar_role.configure(text=f"Rôle : {self.current_user_role}", text_color="white")  # Afficher le rôle

    def update_tab_access(self):
        """Met à jour l'accès aux onglets en fonction de l'utilisateur."""
        if self.user_identified is None:
            self.users_button.configure(state="disabled")
            self.reduire_button.configure(state="disabled")
            self.ajouter_button.configure(state="disabled")
            self.settings_button.configure(state="disabled")
        else:
            user_role = self.authorized_users[self.user_identified]["role"]
            self.current_user_role = user_role  # Mettre à jour le rôle de l'utilisateur
            if user_role == "administrateur":
                self.reduire_button.configure(state="normal")
                self.ajouter_button.configure(state="normal")
                self.users_button.configure(state="normal")
                self.produit_button.configure(state="normal")
                self.settings_button.configure(state="normal")
            else:
                self.reduire_button.configure(state="normal")
                self.ajouter_button.configure(state="normal")

    def reset_inactivity_timer(self, event=None):
        self.inactivity_timeout = 300

    def check_inactivity(self):
        """Vérifie l'inactivité toutes les secondes."""

        self.inactivity_timeout -= 1

        if self.inactivity_timeout == 0:
            print("logout")
            self.logout()  # Appelle la fonction de déconnexion après inactivité
        elif self.user_identified is not None:  # Si un utilisateur est connecté et que l'inactivité n'a pas dépassé le timeout
            # Vérifie à nouveau après 1000 ms (1 seconde)
            self.after(1000, self.check_inactivity)


    def login(self, username):
        """Cette fonction sera appelée lors de la connexion d'un utilisateur"""
        # Logique de connexion de l'utilisateur
        print("connexion login")
        self.user_identified = username
        self.current_user_name = self.authorized_users[username]["nom"]
        self.current_user_role = self.authorized_users[username]["role"]

        # Mettre à jour l'interface après la connexion
        self.update_sidebar_status()
        self.update_tab_access()

        self.check_inactivity()


    def logout(self):
        """Déconnecte l'utilisateur et réinitialise l'interface."""
        self.user_identified = None
        self.current_user_name = ""
        self.update_sidebar_status()
        self.update_tab_access()
        self.produits_scannes_r = {}
        self.produits_scannes_a = {}

        if self.current_tab != "dashboard":
            show_dashboard(self.main_view)

        # Arrêter la vérification de l'inactivité
        self.reset_inactivity_timer()
        print("Utilisateur déconnecté.")


    def handle_barcode(self):
        """Gère le scan du code-barres et la navigation entre les onglets."""

        scanned_code = self.scan_code.strip()
        self.reset_inactivity_timer()
        username = self.current_user_name
        print(f"Code scanné : {scanned_code}")
        print(f"Tab actuelle = {self.current_tab}")

        if scanned_code == "LOGOUT":
            self.logout()
            self.scan_code = ""
            return

        if self.user_identified is None:
            if scanned_code in self.authorized_users:
                self.login(scanned_code)
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


        # Dictionnaire pour mapper les codes scannés aux actions
        tab_scan = {
            "ACC001": ("dashboard", show_dashboard),
            "RED001": ("sortie", show_sortie),
            "AJT001": ("entree", show_entree),
            "SCANPROD": ("scan_prod", lambda view: show_all_products(view, username)),
            "COMMAND": ("commande", show_users),
            "USERS": ("users", show_users),
            "SETTINGS": ("settings", show_settings),
        }

        # Vérification de l'onglet actuel
        if scanned_code in tab_scan:
            self.current_tab, action = tab_scan[scanned_code]
            action(self.main_view)

    def on_press_button(self, choix):


        self.reset_inactivity_timer()
        username = self.current_user_name

        # Dictionnaire pour mapper les codes scannés aux actions
        tab_button = {
            "dash": ("dashboard", show_dashboard),
            "sortie": ("sortie", show_sortie),
            "ajouter": ("entree", show_entree),
            "prod": ("scan_prod", lambda view: show_all_products(view, username)),
            "command": ("commande", show_commande),
            "users": ("users", show_users),
            "settings": ("settings", show_settings),
        }

        # Vérification de l'onglet actuel
        if choix in tab_button:
            self.current_tab, action = tab_button[choix]
            action(self.main_view)


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
