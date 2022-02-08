import config
from web3 import Web3
from flask import Flask, render_template
import requests


app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(config.INFURA_URL))

@app.route("/")
def index():
    result = requests.get(config.url, headers=config.headers, params=config.payload).json()
    return render_template("index.html", result=result)

@app.route("/address/<addr>")
def address(addr):
    return render_template("address.html", addr=addr)

@app.route("/block/<block_number>")
def block(block_number):
    return render_template("block.html", block_number=block_number)

@app.route("/tx/<hash>")
def transaction(hash):
    transaction = w3.eth.get_transaction(hash)
    return render_template("transaction.html", hash=hash, transaction=transaction)
