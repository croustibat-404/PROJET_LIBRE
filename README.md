# PROJET_LIBRE
Projet libre de web. Site web d'une banque (UQAC Bank).

Technologies : HTML, CSS, JavaScript, Python (back-end Flask).

## Prérequis

- [Python 3.10+](https://www.python.org/downloads/) (vérifier avec `python --version`)
- Git

## Installation (à faire une seule fois)

1. Cloner le dépôt et se placer dans le dossier :

   ```bash
   git clone https://github.com/croustibat-404/PROJET_LIBRE.git
   cd PROJET_LIBRE
   ```

2. Créer l'environnement virtuel :

   ```bash
   python -m venv .venv
   ```

3. Activer l'environnement virtuel :

   | Système | Commande |
   |---|---|
   | Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
   | Windows (cmd) | `.venv\Scripts\activate.bat` |
   | macOS / Linux | `source .venv/bin/activate` |

   `(.venv)` doit apparaître au début de la ligne du terminal.

   > **Windows PowerShell :** si l'activation est bloquée ("l'exécution de scripts est désactivée"),
   > lancer une fois `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
   > puis recommencer. Sinon, utiliser `cmd` avec la commande `.bat`.
   >
   > **macOS / Linux :** si `python` n'est pas reconnu, utiliser `python3`.

4. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Lancer le site

Avec l'environnement virtuel activé :

```bash
flask --app app run --debug
```

Puis ouvrir http://127.0.0.1:5000/ dans le navigateur.
Le serveur se recharge automatiquement quand on modifie le code. Arrêt : `Ctrl + C`.

## À chaque reprise du travail

```bash
git pull
.venv\Scripts\Activate.ps1      # (ou la commande de votre système)
pip install -r requirements.txt # utile si quelqu'un a ajouté une dépendance
```

## Structure du projet

| Dossier / fichier | Rôle |
|---|---|
| `app.py` | Routes et logique back-end (Flask) |
| `templates/` | Pages HTML (moteur Jinja2) |
| `static/css/`, `static/js/`, `static/img/` | CSS, JavaScript, images |
| `bdd/` | Base de données |
| `requirements.txt` | Liste des dépendances Python |

## Règles d'équipe

- Ne jamais committer `.venv/` (déjà dans le `.gitignore`).
- Si on installe une nouvelle bibliothèque (`pip install ...`), mettre à jour la liste et la committer :

  ```bash
  pip freeze | Out-File -Encoding utf8 requirements.txt   # PowerShell
  pip freeze > requirements.txt                           # macOS / Linux / cmd
  ```