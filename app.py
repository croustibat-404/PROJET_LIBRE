import hmac
import os
import re
import secrets
import sqlite3
from pathlib import Path

from flask import (Flask, abort, flash, redirect, render_template,
request, session, url_for)
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
BDD_PATH = BASE_DIR / "bdd" / "bdd.db"
SCHEMA_PATH = BASE_DIR / "bdd" / "schema.sql"

LONGUEUR_NUMERO_CLIENT = 8     # identifiant de connexion du client
LONGUEUR_NUMERO_COMPTE = 11
LONGUEUR_MIN_MDP = 8
LONGUEUR_MAX_MDP = 128
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TEL_RE = re.compile(r"^\+?[\d\s().-]{6,20}$")

app = Flask(__name__)
# Clé qui signe le cookie de session. En production : variable d'environnement SECRET_KEY.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def ouvrir_bdd():
    conn = sqlite3.connect(BDD_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    return conn, cursor

def crea_table_bdd():
    conn, cursor = ouvrir_bdd()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as fichier:
            cursor.executescript(fichier.read())
        conn.commit()
    finally:
        conn.close()

crea_table_bdd()

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]

app.jinja_env.globals["csrf_token"] = csrf_token

@app.before_request
def verifier_csrf():
    if request.method == "POST":
        recu = request.form.get("csrf_token", "")
        attendu = session.get("csrf", "")
        if not attendu or not hmac.compare_digest(recu, attendu):
            abort(400)

def generer_numero_unique(cursor, table, colonne, longueur):
    """Tire un numéro aléatoire (avec des zéros devant si besoin) jusqu'à en trouver un libre.
    `table` et `colonne` viennent du code, jamais de l'utilisateur (sinon : injection SQL)."""
    while True:
        numero = f"{secrets.randbelow(10 ** longueur):0{longueur}d}"
        cursor.execute(f"SELECT 1 FROM {table} WHERE {colonne} = ?", (numero,))
        if cursor.fetchone() is None:
            return numero

def email_existe(email):
    conn, cursor = ouvrir_bdd()
    try:
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def valider_inscription(donnees, mot_de_passe, confirmation):
    """Retourne la liste des messages d'erreur (liste vide = tout est valide).
    Le navigateur valide aussi (required, type=email...) mais on ne s'y fie JAMAIS :
    n'importe qui peut envoyer une requête POST sans passer par notre formulaire."""
    erreurs = []
    for cle, libelle in (("prenom", "Le prénom"), ("nom", "Le nom")):
        if not donnees[cle]:
            erreurs.append(f"{libelle} est obligatoire.")
        elif len(donnees[cle]) > 100:
            erreurs.append(f"{libelle} est trop long (100 caractères max).")

    if not EMAIL_RE.match(donnees["email"]) or len(donnees["email"]) > 254:
        erreurs.append("L'adresse e-mail n'est pas valide.")

    if donnees["phone"] and not TEL_RE.match(donnees["phone"]):
        erreurs.append("Le numéro de téléphone n'est pas valide.")

    if not LONGUEUR_MIN_MDP <= len(mot_de_passe) <= LONGUEUR_MAX_MDP:
        erreurs.append(f"Le mot de passe doit contenir entre {LONGUEUR_MIN_MDP} "
                    f"et {LONGUEUR_MAX_MDP} caractères.")
    elif mot_de_passe != confirmation:
        erreurs.append("Les deux mots de passe ne correspondent pas.")
    return erreurs

def creer_utilisateur(donnees, mot_de_passe):
    """Crée le client ET son compte courant dans UNE transaction :
    soit les deux existent, soit aucun. Retourne le numéro client (identifiant de connexion)."""
    conn, cursor = ouvrir_bdd()
    try:
        numero_client = generer_numero_unique(cursor, "users", "client_number", LONGUEUR_NUMERO_CLIENT)
        numero_compte = generer_numero_unique(cursor, "accounts", "account_number", LONGUEUR_NUMERO_COMPTE)
        cursor.execute(
            "INSERT INTO users (client_number, first_name, last_name, email, phone, password_hash) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (numero_client, donnees["prenom"], donnees["nom"], donnees["email"],
            donnees["phone"] or None,                      # vide -> NULL en base
            generate_password_hash(mot_de_passe)),         # on stocke l'empreinte, jamais le mot de passe
        )
        cursor.execute(
            "INSERT INTO accounts (user_id, type, account_number) VALUES (?, 'checking', ?)",
            (cursor.lastrowid, numero_compte),
        )
        conn.commit()
        return numero_client
    finally:
        conn.close()

@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/connexion")
def login():
    return render_template("connexion.html")


@app.route("/inscription", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("inscription.html", erreurs=[], form={})

    donnees = {cle: request.form.get(cle, "").strip()
            for cle in ("nom", "prenom", "email", "phone")}
    donnees["email"] = donnees["email"].lower()
    mot_de_passe = request.form.get("password", "")
    confirmation = request.form.get("password_confirm", "")

    erreurs = valider_inscription(donnees, mot_de_passe, confirmation)
    if not erreurs and email_existe(donnees["email"]):
        erreurs.append("Un compte existe déjà avec cette adresse e-mail.")

    if not erreurs:
        try:
            numero_client = creer_utilisateur(donnees, mot_de_passe)
        except sqlite3.IntegrityError:
            erreurs.append("Un compte existe déjà avec cette adresse e-mail.")

    if erreurs:
        return render_template("inscription.html", erreurs=erreurs, form=donnees), 400

    flash(f"Compte créé ! Votre identifiant client est {numero_client}. "
        "Notez-le : il vous servira à vous connecter.")
    return redirect(url_for("login"))