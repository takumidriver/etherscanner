import config
from web3 import Web3
from flask import Flask, render_template
import requests, time


app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(config.INFURA_URL))



@app.route("/")
def index():
    result = requests.get(config.url, headers=config.headers, params=config.payload).json()
    latest_blocks = []
    for block_number in range(w3.eth.block_number, w3.eth.block_number-10, -1):
        block = w3.eth.get_block(block_number)
        latest_blocks.append(block)

    latest_transactions = []
    for tx in latest_blocks[-1]['transactions'][-10:]:
        transaction = w3.eth.get_transaction(tx)
        latest_transactions.append(transaction)
    current_time = time.time()
    return render_template("index.html", result=result['USD'],
    latest_blocks=latest_blocks,
    latest_transactions=latest_transactions,
    current_time = current_time)

@app.route("/address/<addr>")
def address(addr):
    balance = w3.eth.get_balance(addr)
    ether_balance = w3.fromWei(balance, 'ether')
    current_price = requests.get(config.url, headers=config.headers, params=config.payload).json()
    current_value = "${:,.2f}".format(current_price['USD'] * float(ether_balance))
    return render_template("address.html", addr=addr, ether_balance=ether_balance, current_value=current_value)

@app.route("/block/<block_number>")
def block(block_number):
    block = w3.eth.get_block(int(block_number))
    return render_template("block.html", block=block)

@app.route("/tx/<hash>")
def transaction(hash):
    transaction = w3.eth.get_transaction(hash)
    amount = w3.fromWei(transaction.value, 'ether')
    current_price = requests.get(config.url, headers=config.headers, params=config.payload).json()
    current_value = (current_price['USD'] * float(amount))
    return render_template("transaction.html", amount=amount,
        hash=hash,
        transaction=transaction,
        current_value=current_value)

@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')

@app.template_filter()
def length(content):
    return len(content)

#CHECK OUT REDIS FOR CACHING LAYER
