from web3 import Web3
from flask import Flask, render_template
import requests, time, redis, json, asyncio, config, price

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(config.INFURA_URL))

data = redis.Redis(host='127.0.0.1', port=6379, db=0)

@app.route("/")
def index():
    print("TEST")
    pyth_results = asyncio.run(price.get_price())
    current_eth_price = data.get('current_eth_price')

    if current_eth_price is None:
        current_eth_price = requests.get(config.url, headers=config.headers, params=config.payload).json()
        data.set('current_eth_price', Web3.toJSON(current_eth_price['USD']), ex=200)

    new_blocks = data.hgetall('latest_blocks')

    if new_blocks is None:
        x = 1

    latest_blocks = []
    latest_transactions = []
    for block_number in range(w3.eth.block_number, w3.eth.block_number-10, -1):
        block = w3.eth.get_block(block_number)
        latest_blocks.append(block)
        block_string = Web3.toJSON(block)

    for tx in latest_blocks[-1]['transactions'][-10:]:
        transaction = w3.eth.get_transaction(tx)
        latest_transactions.append(transaction)
        tx_info = Web3.toJSON(latest_transactions)
        tx_string = Web3.toJSON(tx)
        tx_string = tx_string.strip("\"")
        data.hset(block_number, tx_string, tx_info)




    current_time = time.time()
    return render_template("index.html", current_eth_price=data.get('current_eth_price').decode('utf-8'),
    latest_blocks= latest_blocks,
    latest_transactions=latest_transactions,
    current_time = current_time,
    data = data,
    pyth_results=pyth_results)

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

@app.template_filter()
def decodeToUTF(content):
    return content.decode('utf-8')

#CHECK OUT REDIS FOR CACHING LAYER
