from hashlib import sha256
import json
import time
import random
import pymongo
import rsa, base64
import requests

nodes_server_addrs = []
ADDR1 = "http://localhost:8001"
ADDR2 = "http://localhost:8002"
nodes_server_addrs.append(ADDR1)
nodes_server_addrs.append(ADDR2)


class Block:
    def __init__(self,BID,transactions,preblock):
        self.BID = BID                              # Identification for each block
        self.transactions = transactions            # Transactions stored in the block, for our program we have the context, author and posting time
        self.timestamp = time.time()                # Timestamp when this block is created
        self.preblock = preblock                    # To fullfill a blockchain, we need to know the previous block
        self.random_digit = random.randint(0,10000) # To make sure the hash value fit our requirments
    
    def compute_hash(self):
        '''
        To make sure the block can not be changed we compute the hash of the block
        '''
        block_json = json.dumps(self.__dict__)
        return sha256(block_json.encode()).hexdigest()
    
    @property
    def hash(self):
        '''
        To make sure it is hard to reconstruction the whole chain
        with a low price, we set some criteria to the hash value.
        Here we want the hash value would start with two 00
        '''
        hash_value = self.compute_hash()
        while not hash_value.startswith('00'):
            self.random_digit += 1
            hash_value = self.compute_hash()
        return hash_value

class BlockChain:
    def __init__(self):
        self.new_transactions = []
        self.chain = []
        self.initial_chain()

    def create_origin_block(self):
        '''
        To create a Blockchain the first block should be created
        by the server.
        '''
        origin_block_json = []
        origin_block_json.append(json.dumps({"author":"God", "content":"Hello World!"}))
        origin_block = Block(0,origin_block_json,"none")
        self.chain.append(origin_block)
        self.DB_update(origin_block)
        #print('create origin block')
    
    @property
    def last_block(self):
        return self.chain[-1]

    def initial_chain(self):
        '''
        Go to check if we have a chain in database.
        If we do, use that chain
        If we don't, create a new 
        '''
        #print('initial_chain')
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.test
        collection = db.BlockChain

        result = collection.find_one({'BID':0})
        #print(not result)
        if not result:
            self.create_origin_block()
            return "Create an original block"

        '''
        check hash to make sure the chain in database is a valid chain
        '''
        chain = collection.find()
        for block in chain:
            new_B = Block(block['BID'],block['transac'],block['preblock'])
            new_B.timestamp = block['time']
            #print(block['random_digit'])
            new_B.random_digit = block['random_digit']
            #print(new_B.random_digit)
            if new_B.hash == block['hash']:
                self.chain.append(new_B)
            else:
                return "Invalid chain"
        
        '''
        check if we have the longest valid chain
        '''
        longest_chain = self.nodes_chain_check()
        if longest_chain:
            print('long')
            self.chain = longest_chain

        return "Load an existed chain"

    @classmethod
    def check_block(cls, block):
        '''
        To make sure the block is valid for our block chain
        we have two criteria
        (1) The hash value should be the same with the return of
        compute_hash()
        (2) The hash value should start with '00'
        ''' 
        return (block.hash.startswith('00') and 
                block.hash == block.compute_hash())

    def add_newblock(self, block):
        '''
        To add a new block into the chain, we need to make sure 
        the block was insert to the chain in order and the block
        is valid.
        Also, to make it easier to check if this new block is
        added or not, we ask this function to have a bool output.
        '''
        if block.preblock != self.last_block.hash:
            #print('1')
            return False
        
        if block.hash != block.compute_hash():
            #print('2')
            return False
        
        self.chain.append(block)
        self.DB_update(block)

        return True
    
    def add_transaction(self, transaction):
        '''
        This function is to temporatliy saved the new transaction
        '''
        self.new_transactions.append(transaction)

    def mine(self):
        '''
        This function is used to create a new block and insert 
        it into the whole chain.
        '''
        if self.new_transactions == []:
            return False
        
        new_block_ID = self.last_block.BID + 1
        preblock_hash = self.last_block.hash

        new_block = Block(new_block_ID, self.new_transactions, preblock_hash)
        
        if self.add_newblock(new_block):
            self.new_transactions = []
            return self.last_block.BID
        else:
            return False
    
    def DB_update(self, new_block):
        '''
        To make sure we can keep the contents after the server is offline
        '''
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.test
        collection = db.BlockChain

        insert_block = {
            'BID': new_block.BID,
            'transac': new_block.transactions,
            'time': new_block.timestamp,
            'random_digit': new_block.random_digit,
            'preblock': new_block.preblock,
            'hash': new_block.hash
        }

        collection.insert(insert_block)
    
    def nodes_chain_check(self):
        '''
        To make sure the chain we loaded are the longest chain,
        which is also the chain includes most block.
        '''
        current_length = len(self.chain)
        new_chain = False

        for addr in nodes_server_addrs:
            try:
                response = requests.get('{}/chain'.format(addr))
            except requests.exceptions.ConnectionError:
                continue
            else:
                if response.status_code == 200:
                    new_len = response.json()['length']
                    if new_len > current_length:
                        current_length = new_len
                        new_chain = response.json()['chain']
        
        if new_chain:
            return new_chain
        
        return False
            



'''
Now we deploy the blockchain framework to a flask server
'''
from flask import Flask, request, redirect

app = Flask(__name__)

BCChat = BlockChain()

# connect to the database
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.test
collec_User = db.User

@app.route('/')
def Hello():
    #print(test())
    if not BCChat.new_transactions:
        print('None')
    print(BCChat.new_transactions)
    return 'Hello Hello'

@app.route('/add_new_transaction', methods=['POST'])
def add_new_transaction():
    '''
    Provide a interface to client to add new transaction to
    the block chain.
    '''
    new_transaction = request.get_json()
    #new_transactions = {'author':'ReallyMonkey','content':'testtesttest',}
    new_posts = ["author", "content", "signature"]

    # To make sure we have the valid input content
    for post in new_posts:
        if not new_transaction.get(post):
            result = "Missing " + post
            return result, 404
    
    # Also, we need to have an authentication of author's identity
    if not check_sig(new_transaction):
        return "signature not valid", 404
    
    BCChat.add_transaction(new_transaction)
    #print(BCChat.new_transactions)

    return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    '''
    To show the whole chain, we need this function to responese
    the whole chain to the application who requires the blockchain
    '''
    whole_chain = []
    for block in BCChat.chain:
        whole_chain.append(block.__dict__)
    return json.dumps({"length":len(whole_chain), "chain":whole_chain})

@app.route('/mine', methods=['GET'])
def app_mine():
    result = BCChat.mine()
    if not result:
        return "No transaction to mine"
    return "Block #{} has been mined.".format(result)

def check_sig(new_transaction):
    user_info = collec_User.find_one({'name':new_transaction['author']})
    pub_key = user_info['public'].encode()
    public_key = rsa.PublicKey.load_pkcs1(pub_key)
    sig_bytes = bytes(new_transaction['signature'], encoding='utf-8')
    signature = base64.b64decode(sig_bytes)
    transac_body = {
        'author': new_transaction['author'],
        'content': new_transaction['content'],
        'time': new_transaction['time']
    }
    transac_json = json.dumps(transac_body).encode()
    try:
        rsa.verify(transac_json, signature, public_key)
    except rsa.pkcs1.VerificationError:
        return False
    else:
        return True

# Run app
app.run(debug=True, port=8000)

