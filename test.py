import config
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(config.INFURA_URL))

print(w3.eth.block_number)

balance = w3.eth.get_balance('0x15F2636c01d0F43f1F04D22361b8D8d02D27669A')
print(balance)
ether_balance = w3.fromWei(balance, 'ether')
print(ether_balance)

transaction = w3.eth.get_transaction('0x66ecac3f18d32b1efbd3603d8582eb6228a7a20b6a6875014c89db7f24cee74c')
print(transaction)
