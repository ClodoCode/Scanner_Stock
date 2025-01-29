import tkinter as tk
import customtkinter as ctk
from PIL import Image
import json
from app import Application
from fonction import load_users_from_json

class Login(ctk.CTk):
    def __init__(self, authorized_users):
        super().__init__()
        self.title("Login")
        self.geometry("600x480")
        self.resizable(0, 0)

        global frame, label_status


        self.authorized_users = authorized_users

        
        # Variables pour le design
        side_img_data = Image.open("side-img.png")
        side_img = ctk.CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))

        # Création de l'interface de la fenêtre
        ctk.CTkLabel(master=self, text="", image=side_img).pack(expand=True, side="left")
        frame = ctk.CTkFrame(master=self, width=300, height=480, fg_color="#ffffff")
        frame.pack_propagate(0)
        frame.pack(expand=True, side="right")

        # Titre et message de bienvenue
        ctk.CTkLabel(master=frame, text="Bienvenue!", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))
        ctk.CTkLabel(master=frame, text="Entrez votre code utilisateur", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", padx=(25, 0))

        # Champ de texte pour entrer le code utilisateur
        self.username_entry = ctk.CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
        self.username_entry.pack(anchor="w", pady=(38, 0), padx=(25, 0))

        # Lier l'événement de la touche "Entrée" pour valider le login
        self.username_entry.bind("<Return>", self.authenticate)

        # Bouton de connexion
        ctk.CTkButton(master=frame, text="Se connecter", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=self.authenticate).pack(anchor="w", pady=(40, 0), padx=(25, 0))

        label_status = ctk.CTkLabel(frame, text="", font=("Arial", 18, "italic"), text_color="red")
        label_status.pack(pady=(50, 15), anchor="center")

        ctk.CTkButton(master=frame, text="Quitter", fg_color="#CCCCCC", text_color="#000000", hover_color="#AAAAAA", width=225, command=self.destroy).pack(anchor="w", pady=(10, 0), padx=(25, 0))


        # Variable pour vérifier si l'utilisateur est connecté
        self.user_identified = None


    def authenticate(self):
        # Fonction pour vérifier les identifiants
        users = load_users_from_json("users.json")
        username = self.username_entry.get().strip()
        
        # Vous pouvez ajouter une logique pour vérifier l'utilisateur
        # Ici, nous supposons simplement qu'il y a une liste d'utilisateurs autorisés
        if self.is_valid_user(username):
            print("Connexion réussie")
            self.destroy()  # Fermer la fenêtre de connexion
            self.open_main_application()
        else:
            print("Échec de la connexion")

    def is_valid_user(self, userid):

        if userid in self.authorized_users:
            return True
        return False


    def open_main_application(self):
        # Lancer l'application principale après une connexion réussie
        app = Application()
        app.mainloop()

if __name__ == "__main__":
    login_window = Login()
    login_window.mainloop()