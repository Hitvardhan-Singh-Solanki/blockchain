# -*- coding: utf-8 -*-

"""
Created on Thu Mar 21 17:24:23 2019

@author: Hitvardhan.Solanki
"""
import datetime
import hashlib
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse
from flask import Flask, jsonify, request


# 1. Building the Cryptocurrency

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof=1, prev_hash='0')

    def create_block(self, proof, prev_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof == False:
            hash_ops = hashlib.sha256(
                str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_ops[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_ops = hashlib.sha256(
                str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_ops[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True

    def add_transactions(self, sender, receiver, amt):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amt
        })
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1

    def addNode(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if(response.status_code == 200):
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True

        return False


# 2. Mining the block chain
app = Flask(__name__)


# Creating an address on PORT 5050

node_address = str(uuid4()).replace('-', '')

# Creating a web app

blockchain = Blockchain()


# Mining a new block

@app.route('/mine_block', methods=['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transactions(
        sender=node_address, receiver='Hitvardhan', amt=1)
    block = blockchain.create_block(proof, prev_hash)
    response = {'message': 'Congrats!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'transactions': block['transactions']}

    return jsonify(response), 200

# Get the full block chain


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

# Check for valid chain


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {
        'isChainValid': blockchain.is_chain_valid(blockchain.chain),
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

# Add transactions in the block chain


@app.route('/add_trx', methods=['POST'])
def add_trx():
    json = request.get_json()
    trx_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in trx_keys):
        return 'THIK SE BHEJ CHUTIYE', 400
    index = blockchain.add_transactions(
        sender=json['sender'],
        receiver=json['receiver'],
        amt=json['amount']
    )

    response = {
        'message': f'This trx will be added to the block {index}'
    }

    return jsonify(response), 201

# 3. Decentralization

# Connecting the new node


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No nodes", 400
    for node in nodes:
        blockchain.addNode(address=node)
    response = {
        'message': 'Nodes created and added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

# Replacing the chain with the longest chain if required


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    replaced = blockchain.replace_chain()
    if replaced:
        response = {
            'message': 'The chain is replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {'message': 'the chain is up-to-date',
                    'original_chain': blockchain.chain}

    return jsonify(response), 200


# Run the app
app.run(host='localhost', port=5050)
