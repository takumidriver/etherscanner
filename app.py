from web3 import Web3
from flask import Flask, render_template
import requests, time, redis, json, asyncio, config, price

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(config.INFURA_URL))

data = redis.Redis(host='127.0.0.1', port=6379, db=0)

@app.route("/")
def index():
    recash = []
    cached_blocks = []
    pyth_results = data.get('current_btc_price')
    if pyth_results is None:
        pyth_results = asyncio.run(price.get_price())
        data.set('current_btc_price', round(pyth_results['price'], 2), ex=15)

    current_eth_price = data.get('current_eth_price')
    if current_eth_price is None:
        current_eth_price = requests.get(config.url, headers=config.headers, params=config.payload).json()
        data.set('current_eth_price', Web3.toJSON(current_eth_price['USD']), ex=15)

    latest_blocks = []
    latest_transactions = []
    for block_number in range(w3.eth.block_number, w3.eth.block_number-2, -1):
        block = w3.eth.get_block(block_number)
        latest_blocks.append(block)
        block_string = Web3.toJSON(block)
        data.hset('blocks', block_number, block_string)

    for tx in latest_blocks[-1]['transactions'][-3:]:
        transaction = w3.eth.get_transaction(tx)
        latest_transactions.append(transaction)
        tx_info = Web3.toJSON(transaction)
        tx_string = Web3.toJSON(tx)
        tx_string = tx_string.strip("\"")
        data.hset('transactions', tx_string, tx_info)


    for block in data.hkeys('blocks'):
        content = data.hget('blocks', block)
        block_data = json.loads(content)
        x = (block_data['number'], block_data)
        cached_blocks.append(x)
        cached_blocks.sort()
        cached_blocks.reverse()
        recash = []
    [recash.append(x) for x in cached_blocks if x not in recash]

    while(len(recash) > 10):
        recash.pop((len(recash)-1))


    current_time = time.time()
    current_eth_price=data.get('current_eth_price').decode('utf-8')
    return render_template("index.html", current_eth_price=current_eth_price,
    latest_blocks= latest_blocks,
    latest_transactions=latest_transactions,
    current_time = current_time,
    data = data,
    cached_blocks = recash)

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

@app.template_filter()
def decodeTransaction(content):
    block_data = json.loads(content)
    return block_data['blockNumber']

@app.template_filter()
def getBlockNumber(content):
    block_data = json.loads(content)
    cached_blocks.append((block_data['number'], block_data))
    cached_blocks.sort()
    return

#CHECK OUT REDIS FOR CACHING LAYER
