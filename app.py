from flask import Flask, render_template, url_for, redirect
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BDD_PATH = BASE_DIR / "bdd" / "bdd.db"
SCHEMA_PATH = BASE_DIR / "bdd" / "schema.sql"

app = Flask(__name__)

@app.route("/")
def accueil():
    return render_template("index.html")

@app.route("/connexion")
def login():
    return render_template("connexion.html")

@app.route("/inscription")
def register():
    return render_template("inscription.html")
    

def ouvrir_bdd():
    conn = sqlite3.connect(BDD_PATH)
    
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    return conn, cursor
    
def crea_table_bdd():
    conn, cursor = ouvrir_bdd()
    try :
        with open(SCHEMA_PATH, "r", encoding="utf-8") as fichier:
            sql_script = fichier.read()
            cursor.executescript(sql_script)
        conn.commit()
    finally:
        conn.close()
        
crea_table_bdd()