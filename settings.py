import json
import os
import tkinter as tk
from customtkinter import *

# Chemin du fichier de configuration
CONFIG_FILE = "settings_config.json"

# Fonction pour charger les paramètres sauvegardés
def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {
        "theme": "Dark",
        "font_size": "Medium",
        "primary_color": "#1f6aa5"
    }

# Fonction pour sauvegarder les paramètres
def save_settings(settings):
    with open(CONFIG_FILE, "w") as file:
        json.dump(settings, file, indent=4)

# Fonction pour afficher la page des paramètres
def show_settings(main_view):
    """Affiche une page de paramètres avec une interface moderne et responsive."""
    # Effacer les widgets existants
    for widget in main_view.winfo_children():
        widget.destroy()

    # Charger les paramètres existants
    settings = load_settings()

    # --- Conteneur principal ---
    settings_frame = CTkFrame(main_view, fg_color="#2a2d32", corner_radius=20)
    settings_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # --- Titre ---
    title_label = CTkLabel(settings_frame, text="⚙️ Paramètres", font=("Arial Bold", 22), text_color="white")
    title_label.pack(pady=20)

    # --- Option Thème (Clair / Sombre) ---
    theme_var = tk.StringVar(value=settings["theme"])
    theme_frame = CTkFrame(settings_frame, fg_color="transparent")
    theme_frame.pack(fill="x", padx=20, pady=5)

    theme_label = CTkLabel(theme_frame, text="🌗 Thème :", font=("Arial", 16), text_color="white")
    theme_label.pack(side="left", padx=10)

    theme_menu = CTkOptionMenu(theme_frame, values=["Light", "Dark"], variable=theme_var, width=120)
    theme_menu.pack(side="right", padx=10)

    # --- Option Taille de Police ---
    font_var = tk.StringVar(value=settings["font_size"])
    font_frame = CTkFrame(settings_frame, fg_color="transparent")
    font_frame.pack(fill="x", padx=20, pady=5)

    font_label = CTkLabel(font_frame, text="🔠 Taille de police :", font=("Arial", 16), text_color="white")
    font_label.pack(side="left", padx=10)

    font_menu = CTkOptionMenu(font_frame, values=["Small", "Medium", "Large"], variable=font_var, width=120)
    font_menu.pack(side="right", padx=10)

    # --- Sélection de la couleur principale ---
    color_var = tk.StringVar(value=settings["primary_color"])
    color_frame = CTkFrame(settings_frame, fg_color="transparent")
    color_frame.pack(fill="x", padx=20, pady=5)

    color_label = CTkLabel(color_frame, text="🎨 Couleur principale :", font=("Arial", 16), text_color="white")
    color_label.pack(side="left", padx=10)

    color_entry = CTkEntry(color_frame, textvariable=color_var, width=120)
    color_entry.pack(side="right", padx=10)

    # --- Fonction de sauvegarde ---
    def save_and_apply():
        settings["theme"] = theme_var.get()
        settings["font_size"] = font_var.get()
        settings["primary_color"] = color_var.get()
        save_settings(settings)

        # Appliquer le thème immédiatement
        set_appearance_mode(settings["theme"].lower())

    # --- Fonction pour réinitialiser les paramètres ---
    def reset_settings():
        theme_var.set("Dark")
        font_var.set("Medium")
        color_var.set("#1f6aa5")
        save_and_apply()

    # --- Boutons Sauvegarde et Réinitialisation ---
    button_frame = CTkFrame(settings_frame, fg_color="transparent")
    button_frame.pack(pady=20, fill="x", padx=20)

    save_button = CTkButton(button_frame, text="💾 Sauvegarder", command=save_and_apply, height=40, corner_radius=10)
    save_button.pack(side="left", expand=True, padx=5)

    reset_button = CTkButton(button_frame, text="🔄 Réinitialiser", fg_color="red", command=reset_settings, height=40, corner_radius=10)
    reset_button.pack(side="right", expand=True, padx=5)

    # Ajustement dynamique
    settings_frame.columnconfigure(1, weight=1)
