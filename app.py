from flask import Flask, render_template, url_for, redirect

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
    