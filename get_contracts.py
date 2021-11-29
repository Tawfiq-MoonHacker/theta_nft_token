import json
from web3 import Web3
import time 

theta_network = "https://eth-rpc-api.thetatoken.org/rpc"


abi = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "tokenOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "tokens", "type": "uint256"}], "name": "Approval", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "tokens", "type": "uint256"}], "name": "Transfer", "type": "event"}, {"inputs": [], "name": "_totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "tokenOwner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "remaining", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "tokens", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "tokenOwner", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "balance", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "get_name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "get_symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "a", "type": "uint256"}, {"internalType": "uint256", "name": "b", "type": "uint256"}], "name": "safeAdd", "outputs": [{"internalType": "uint256", "name": "c", "type": "uint256"}], "stateMutability": "pure", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "a", "type": "uint256"}, {"internalType": "uint256", "name": "b", "type": "uint256"}], "name": "safeSub", "outputs": [{"internalType": "uint256", "name": "c", "type": "uint256"}], "stateMutability": "pure", "type": "function"}, {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "receiver", "type": "address"}, {"internalType": "uint256", "name": "tokens", "type": "uint256"}], "name": "transfer", "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "sender", "type": "address"}, {"internalType": "address", "name": "receiver", "type": "address"}, {"internalType": "uint256", "name": "tokens", "type": "uint256"}], "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}]

def moveDecimalPoint(num, decimal_places):
    for _ in range(abs(decimal_places)):

        if decimal_places>0:
            num *= 10; #shifts decimal place right
        else:
            num /= 10.; #shifts decimal place left

    return float(num)

#sending eth to other accounts
def transfer_coins(account_send,account_recv,private_key,quantity):
    w3 = Web3(Web3.HTTPProvider(theta_network))

    balance_send = moveDecimalPoint(w3.eth.get_balance(account_send),-18)
    
    if float(quantity) < float(balance_send):
        nonce = w3.eth.getTransactionCount(account_send)
        
        #build a transaction 
        tx = {
              'nonce':nonce,
              'to':account_recv,
              'value':w3.toWei(quantity,'ether'),
              'gas':2000000,
              'gasPrice':w3.toWei('50','gwei')
              
              }
        signed_tx = w3.eth.account.signTransaction(tx,private_key)
    
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        

def get_balance(address,contract):
    w3 = Web3(Web3.HTTPProvider(theta_network))
    
    w3.eth.default_account = address


    greeter = w3.eth.contract(address=contract,abi=abi)
    return greeter.functions.balanceOf(address).call()


def get_symbol(address,contract):
    w3 = Web3(Web3.HTTPProvider(theta_network))
    w3.eth.default_account = address
    
    greeter = w3.eth.contract(address=contract,abi=abi)
    return greeter.functions.get_symbol().call()



def get_name(address,contract):
    w3 = Web3(Web3.HTTPProvider(theta_network))
    
    w3.eth.default_account = address

    greeter = w3.eth.contract(address=contract,abi=abi)
    return greeter.functions.get_name().call()


def get_supply(address,contract):
    w3 = Web3(Web3.HTTPProvider(theta_network))
    
    w3.eth.default_account = address


    greeter = w3.eth.contract(address=contract,abi=abi)
    return greeter.functions.totalSupply().call()    


def transfer(address,to_address,quantity,contract):
    w3 = Web3(Web3.HTTPProvider(theta_network))
    
    w3.eth.default_account = address


    greeter = w3.eth.contract(address=contract,abi=abi)
    return greeter.functions.transfer(to_address,quantity).transact()  

# w3 = Web3(Web3.HTTPProvider(theta_network))
# acct = w3.eth.account.create()
# print(acct.address)
# balance = w3.eth.get_balance(acct.address)
# # balance = moveDecimalPoint(balance,-18)
            
# print(balance)

