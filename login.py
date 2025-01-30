import tkinter as tk
import customtkinter as ctk
import customtkinter
from PIL import Image
import json
from fonction import load_users_from_json

class LoginWindow(customtkinter.CTkToplevel):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.title("Login")
        self.geometry("600x480")
        self.resizable(0, 0)

        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Capture la fermeture

        global frame, label_status

        # Variables pour le design
        side_img_data = Image.open("side-img.png")
        side_img = customtkinter.CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))

        # Création de l'interface de la fenêtre
        customtkinter.CTkLabel(master=self, text="", image=side_img).pack(expand=True, side="left")
        frame = customtkinter.CTkFrame(master=self, width=300, height=480, fg_color="#ffffff")
        frame.pack_propagate(0)
        frame.pack(expand=True, side="right")

        # Titre et message de bienvenue
        customtkinter.CTkLabel(master=frame, text="Bienvenue!", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))
        customtkinter.CTkLabel(master=frame, text="Entrez votre code utilisateur", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", padx=(25, 0))

        # Champ de texte pour entrer le code utilisateur
        self.username_entry = customtkinter.CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
        self.username_entry.pack(anchor="w", pady=(38, 0), padx=(25, 0))

        # Lier l'événement de la touche "Entrée" pour valider le login
        self.username_entry.bind("<Return>", self.on_login_button_click)

        # Bouton de connexion
        customtkinter.CTkButton(master=frame, text="Se connecter", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=self.authenticate).pack(anchor="w", pady=(40, 0), padx=(25, 0))

        label_status = customtkinter.CTkLabel(frame, text="", font=("Arial", 18, "italic"), text_color="red")
        label_status.pack(pady=(50, 15), anchor="center")

        customtkinter.CTkButton(master=frame, text="Quitter", fg_color="#CCCCCC", text_color="#000000", hover_color="#AAAAAA", width=225, command=self.on_closing).pack(anchor="w", pady=(10, 0), padx=(25, 0))


        # Variable pour vérifier si l'utilisateur est connecté
        self.user_identified = None


    def authenticate(self):
        # Fonction pour vérifier les identifiants
        users = load_users_from_json("users.json")
        username = self.username_entry.get().strip()


        if username in users:
            print(f"Connexion réussi")
            self.on_login_success(username)  # Appelle la fonction de connexion
            self.destroy()  # Ferme la fenêtre de connexion
        else:
            label_status.configure(self, text="Identifiants incorrects", text_color="red")


    def on_login_button_click(self, event=None):  # <-- Ajouter event=None

        users = load_users_from_json("users.json")
        username = self.username_entry.get().strip()

        if username in users:
            print(f"Connexion réussi")
            self.on_login_success(username)  # Appelle la fonction de connexion
            self.destroy()  # Ferme la fenêtre de connexion
        else:
            label_status.configure(self, text="Identifiants incorrects", text_color="red")

    def on_closing(self):
        """Ferme l'application complètement si on ferme la fenêtre de login."""
        if self.parent is not None and self.parent.winfo_exists():  # Vérifie si la fenêtre principale existe
            self.parent.quit()  # Ferme l'application principale correctement
        self.destroy()  # Ferme la fenêtre de login
