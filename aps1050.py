from datetime import datetime
import hashlib as hasher
from flask import Flask
from flask import request
import requests
import json
from sys import argv
node = Flask(__name__)


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    #This function is used to print the block's index
    def showBlock(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }

    def hash_block(self):
        sha = hasher.sha256()
        seq = [str(self.index), str(self.timestamp), str(self.data), str(self.previous_hash)]
        sha.update(''.join(seq).encode('utf-8'))
        return sha.hexdigest()


def make_genesis_block():
    """Make the first block in a block-chain."""
    block = Block(index=0,
                  timestamp=datetime.now().isoformat(),
                  data={'proof-of-work': 9, 'transactions': []},
                  previous_hash="0")
    return block


def next_block(pre_block, data=''):
    """Return next block in a block chain."""
    idx = pre_block.index + 1
    block = Block(index=idx,
                  timestamp=datetime.now().isoformat(),
                  data='This is block {}'.format(idx),
                  previous_hash=pre_block.hash)
    return block


 def run_simple_chain():
     """Test creating chain of 15 blocks."""
     blockchain = [make_genesis_block()]
     prev_block = blockchain[0]
     for _ in range(0, 15):
         block = next_block(prev_block, data='Change to anything you want')
         blockchain.append(block)
         prev_block = block
         print('Block {} added to blockchain at {}'.format(block.index, block.timestamp))
         print('Previous block\'s hash: {}'.format(block.previous_hash))
         print('Hash: {}\n'.format(block.hash))


@node.route('/transaction', methods=['POST'])
def transaction():
    if request.method == "POST":
        #extract transaction data from POST request
        transaction = request.get_json()
        #store it in a list
        transactions.append(transaction)

        print('New Transaction')
        print(json.dumps(transaction))
        print(transactions)
        return json.dumps(list(transactions))


def proof_of_work(previous_proof):
    incrementor = previous_proof + 1
    while not (incrementor % 11 == 0 and incrementor % previous_proof == 0):
        incrementor += 1
    return incrementor

@node.route('/mine', methods=['GET'])
def mining():
    last_block = blockchain[-1]
    last_proof = last_block.data['proof-of-work']
    proof = proof_of_work(last_proof)
    transactions.append({"from": "network", "to": miner_address, "amount": 1})   
    mined_block = Block(
        index=last_block.index + 1,
        timestamp=datetime.now().isoformat(),
        data={
            'proof-of-work': proof,
            'transactions': list(transactions)
        },
        previous_hash=last_block.hash
    )

    blockchain.append(mined_block)
    transactions[:] = []
    return json.dumps([i.showBlock() for i in blockchain])


@node.route('/add_node', methods=['POST'])
def add_node():
    n = request.get_json()
    peer_nodes.add(n["node"])
    return json.dumps(list(peer_nodes))


@node.route('/chains', methods=['GET'])
def get_chain():
    chain_to_send = blockchain
    ret = []
    for block in chain_to_send:
        new_block = {
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'hash': block.hash}
        ret.append(new_block)
    return json.dumps(ret)


@node.route('/cur_chain', methods=['GET'])
def cur_chain():
    consensus()
    return get_chain()


def find_new_chains():
    other_chains = []
    for node_url in peer_nodes:
        print(node_url)
        block = requests.get(node_url + "/chains").content
        block = json.loads(block)
        other_chains.append(block)
        print(block)        
    return other_chains


def consensus():
    global blockchain
    other_chains = find_new_chains()
    longest_chain = blockchain
    flag = False
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            flag = True
            longest_chain = chain
    if flag:
        tmp = []
        for i in longest_chain:
            tmp.append(Block(i['index'], i['timestamp'], i['data'], i['hash']))
        blockchain = tmp
        return
    blockchain = longest_chain



if __name__ == "__main__":
    print(argv)
    miner_address = 'miner address ' + str(argv[1])
    blockchain = [make_genesis_block()]
    previous_block = blockchain[0]
    transactions = []
    peer_nodes = set()
    node.run(port=int(argv[1]))


