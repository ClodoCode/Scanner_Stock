# Scanner Stock

Scanner Stock est une application de gestion de stock permettant de suivre et d'organiser les produits à l'aide d'un tableau de bord interactif et de la fonctionnalité de scan des produits.

## Fonctionnalités

- **Gestion des utilisateurs** : Gérez les utilisateurs et attribuez des droits spécifiques.
- **Tableau de bord** : Visualisez les données clés de votre stock en un coup d'œil.
- **Ajout de produits** : Ajoutez ou modifiez des produits dans votre inventaire.
- **Scan des produits** : Scannez les produits à l'aide d'un lecteur de code-barres pour simplifier la gestion des entrées et sorties.

## Structure du projet

Voici un aperçu des principaux fichiers et de leur rôle :

- `app.py` : Fichier principal pour exécuter l'application.
- `dashboard.py` : Gère l'interface utilisateur du tableau de bord.
- `produits.py` : Contient les fonctionnalités liées à la gestion des produits.
- `commande.py` : Gestion des commandes des produits.
- `users.py` : Gère les fonctionnalités liées aux utilisateurs (authentification, gestion des rôles, etc.).
- `entree.py.py` : Gestion des entrées de stock.
- `fonction.py` : Fonctions utilitaires pour l'application.
- `login.py` : Gestion de l'authentification des utilisateurs.
- `sortie.py` : Gestion des sorties de stock.
- `settings.py` : Paramètres globaux de l'application.

## Prérequis

- **Python 3.8+**
- Bibliothèques Python nécessaires (voir `requirements.txt`)

## Installation

1. Clonez ce dépôt sur votre machine locale :

   ```bash
   git clone https://github.com/ClodoCode/Scanner_Stock.git
   ```

2. Accédez au dossier du projet :

   ```bash
   cd Scanner_Stock
   ```

3. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Lancez l'application :

   ```bash
   python app.py
   ```

## Utilisation

1. Connectez-vous avec vos identifiants ou créez un nouvel utilisateur.
2. Accédez au tableau de bord pour consulter l'état actuel de votre stock.
3. Utilisez le scanner de produits pour enregistrer les mouvements d'inventaire.
4. Gérez vos produits et vos utilisateurs via les sections dédiées.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez ajouter des fonctionnalités ou corriger des bugs, veuillez :

1. Forker ce dépôt.
2. Créer une branche pour vos modifications :

   ```bash
   git checkout -b ma-nouvelle-fonctionnalite
   ```

3. Soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Veuillez consulter le fichier `LICENSE` pour plus d'informations.

---

### Remarques

Si vous avez des questions ou des suggestions concernant ce projet, n'hésitez pas à ouvrir une issue ou à me contacter directement.
