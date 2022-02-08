from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "etherscanner!"

@app.route("/tx/<hash>")
def transaction(hash):
    return render_template("transaction.html", hash=hash)
