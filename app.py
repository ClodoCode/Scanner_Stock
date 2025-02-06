from customtkinter import *
import tkinter as tk
import json
from PIL import Image, ImageTk
from dashboard import show_dashboard
from sortie import show_sortie, handle_scan_reduire, get_produits_scannes_r
from entree import show_entree, handle_scan_entree, get_produits_scannes_a
from fonction import load_users_from_json
from produits import show_all_products
from commande import show_commande
from creer import show_creer, handle_scan_cree_command, get_produits_scannes_cc, get_scan_ok
from users import show_users
from settings import show_settings
from login import LoginWindow


class Application(CTk):
    def __init__(self):
        super().__init__()

        # Initialisation de la fenêtre de connexion
        self.withdraw()  # Cache l'interface principale jusqu'à l'authentification
        self.login_window = LoginWindow(self, self.on_login_success)

        # Initialisation des variables
        self.user_identified = None
        self.current_user_name = ""
        self.current_user_role = ""  # Variable pour stocker le rôle de l'utilisateur
        self.scan_code = ""
        self.authorized_users = load_users_from_json("users.json")
        self.current_tab = "dashboard"  # Initialisation de current_tab
        self.produits_scannes_r = get_produits_scannes_r()
        self.produits_scannes_a = get_produits_scannes_a()
        self.produits_scannes_cc = get_produits_scannes_cc()
        self.scan_ok = get_scan_ok()
        self.is_closing = False

        # Configuration de l'interface
        self.configure_window()
        self.create_sidebar()
        self.create_main_view()
        self.update_tab_access()  # Désactiver les onglets au démarrage

        # Lier les événements de pression de touche à la fonction
        self.bind("<Key>", self.capture_keypress)

        self.bind("<Configure>", self.on_resize)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_window(self):
        """Configurer la fenêtre principale de l'application."""
        # Configurer la fenêtre pour être redimensionnable
        self.geometry("1024x768")  # Taille par défaut
        self.resizable(True, True)  # Autoriser le redimensionnement
        self.state("zoomed")  # Maximiser la fenêtre au démarrage

        # Définir le titre et l'icône
        self.title("Logiciel Stock")
        self.iconbitmap("icons/logo.ico")

        # Définir le mode d'apparence
        set_appearance_mode("light")
        self.configure(bg="#2A8C55")

    def on_resize(self, event):
        """Empêche les erreurs de redimensionnement après fermeture."""
        if not self.winfo_exists():  # Vérifie si la fenêtre principale existe encore
            return

        # Vérifie si sidebar_frame et son canvas existent avant de tenter de les redimensionner
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
            try:
                self.sidebar_frame.configure(height=event.height)
            except Exception as e:
                print(f"Erreur lors du redimensionnement: {e}")

    def on_closing(self):
        """Ferme proprement la fenêtre et détruit les widgets avant de quitter."""
        self.unbind("<Configure>")  # Désactive le redimensionnement avant de fermer

        if hasattr(self, 'sidebar_frame') and self.sidebar_frame.winfo_exists():
            self.sidebar_frame.destroy()

        self.after(100, self.quit)
        self.after(200, self.destroy)


    def create_sidebar(self):
        """Créer la barre latérale avec ses éléments."""
        self.sidebar_frame = CTkFrame(master=self, fg_color="#4b5e61", width=176, height=self.winfo_screenheight(), corner_radius=0)
        self.sidebar_frame.pack_propagate(0)
        self.sidebar_frame.pack(fill="y", anchor="w", side="left")

        # Logo
        logo_img_data = Image.open("icons/logo.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(77.68, 85.42))
        CTkLabel(master=self.sidebar_frame, text="", image=logo_img).pack(pady=(38, 8), anchor="center")

        # Section 1 - Menu
        self.menu_section = CTkFrame(self.sidebar_frame, fg_color="transparent", corner_radius=10)
        self.menu_section.pack(fill="x", padx=25, pady=(16, 5))  # Padding pour espacer les sections
        
        # Texte "Menu"
        menu_label = CTkLabel(master=self.menu_section, text="Menu", font=("Arial", 16, "bold"), text_color="white", anchor="center")
        menu_label.pack(pady=(5, 5))

        # Boutons
        self.dashboard_button = self.create_button(self.sidebar_frame, "Dashboard", "icons/package_icon.png", lambda: self.on_press_button("dash"))
        self.users_button = self.create_button(self.sidebar_frame, "Users", "icons/group.png", lambda: self.on_press_button("users"))

        # Section 2 - Catégorie
        self.category_section = CTkFrame(self.sidebar_frame, fg_color="transparent", corner_radius=10)
        self.category_section.pack(fill="x", padx=16, pady=(16, 5))  # Padding pour espacer les sections
        
        # Texte "Catégorie"
        category_label = CTkLabel(master=self.category_section, text="Catégorie", font=("Arial", 16, "bold"), text_color="white", anchor="center")
        category_label.pack(pady=(5, 5))

        username = self.current_user_name

        self.reduire_button = self.create_button(self.sidebar_frame, "Sortie", "icons/logistics_icon.png", lambda: self.on_press_button("sortie"))
        self.ajouter_button = self.create_button(self.sidebar_frame, "Entrée", "icons/delivered_icon.png", lambda: self.on_press_button("ajouter"))
        self.produit_button = self.create_button(self.sidebar_frame, "Produits", "icons/parcel.png", lambda: self.on_press_button("prod"))
        self.creer_button = self.create_button(self.sidebar_frame, "Créer", "icons/product-design.png", lambda: self.on_press_button("creer"))
        self.commande_button = self.create_button(self.sidebar_frame, "Commande", "icons/tracking.png", lambda: self.on_press_button("command"))
        self.settings_button = self.create_button(self.sidebar_frame, "Settings", "icons/gear.png", lambda: self.on_press_button("settings"))

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
        self.logout_button = self.create_button(self.footer_frame, "Déconnexion", "icons/shutdown.png", lambda: self.logout())
        

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
        all_buttons = {
            "users": self.users_button,
            "reduire": self.reduire_button,
            "ajouter": self.ajouter_button,
            "creer": self.creer_button,
            "commande": self.commande_button,
            "produit": self.produit_button,
            "settings": self.settings_button,
        }

        if self.user_identified is None:
            for button in all_buttons.values():
                button.configure(state="disabled")
            return

        self.current_user_role = self.authorized_users[self.user_identified]["role"]

        role_permissions = {
            "administrateur": ["users", "reduire", "ajouter", "creer", "commande", "produit", "settings"],
            "utilisateur": ["reduire", "ajouter", "creer", "commande", "produit", "settings"],
            "invite": ["reduire", "ajouter"]
        }

        allowed_buttons = role_permissions.get(self.current_user_role, [])

        for name, button in all_buttons.items():
            button.configure(state="normal" if name in allowed_buttons else "disabled")


    def on_login_success(self, username):
        """Callback exécuté après une connexion réussie."""
        self.user_identified = username
        self.current_user_name = self.authorized_users[username]["nom"]
        self.current_user_role = self.authorized_users[username]["role"]

        # Mettre à jour l'interface
        self.login(username)  # Connecter l'utilisateur
        self.update_sidebar_status()
        self.update_tab_access()
        self.deiconify()  # Affiche l'application principale


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

        print("Utilisateur déconnecté.")
        #Cacher la fenêtre principale
        self.withdraw()

        # Réafficher la fenêtre de login
        self.login_window = LoginWindow(self, self.on_login_success)
        self.login_window.deiconify()  # S'assurer qu'elle est visible


    def handle_barcode(self):
        """Gère le scan du code-barres et la navigation entre les onglets."""

        scanned_code = self.scan_code.strip()
        username = self.current_user_name
        self.scan_ok = get_scan_ok()

        print(f"Code scanné : {scanned_code}")
        print(f"Tab actuelle = {self.current_tab}")

        if scanned_code == "LOGOUT":
            self.logout()
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

        if self.current_tab == "creer":
            if self.scan_ok =="ok":
                handle_scan_cree_command(scanned_code, username)
                if len(self.produits_scannes_cc) >0:
                    return



        # Dictionnaire pour mapper les codes scannés aux actions
        tab_scan = {
            "ACC001": ("dashboard", show_dashboard),
            "RED001": ("sortie", show_sortie),
            "AJT001": ("entree", show_entree),
            "SCANPROD": ("scan_prod", lambda view: show_all_products(view, username)),
            "COMMAND": ("commande", show_commande),
            "creer": ("creer", show_creer),
            "USERS": ("users", show_users),
            "SETTINGS": ("settings", show_settings),
        }

        # Vérification de l'onglet actuel
        if scanned_code in tab_scan:
            self.current_tab, action = tab_scan[scanned_code]
            action(self.main_view)

    def on_press_button(self, choix):

        username = self.current_user_name

        # Dictionnaire pour mapper les codes scannés aux actions
        tab_button = {
            "dash": ("dashboard", show_dashboard),
            "sortie": ("sortie", show_sortie),
            "ajouter": ("entree", show_entree),
            "prod": ("scan_prod", lambda view: show_all_products(view, username)),
            "command": ("commande", show_commande),
            "creer": ("creer", show_creer),
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