import datetime
import json
import time
import pymongo
import rsa, base64

import requests
from flask import render_template, redirect, request

from app import app

# Connect database
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.test 
collec_User = db.User 

NODES_ADDR = "http://localhost:8000"
posts = []
user = collec_User.find_one({'name':'ReallyMonkey'})
pri_key = user['private']
pub_key = user['public']

@app.route('/login')
def long_in():
    username = request.form['username']
    password = request.form['password']
    user_info = collec_User.find_one({'name':username})
    if not user_info:
        return False

@app.route('/')
def load_index():
    chain_addr = "{}/chain".format(NODES_ADDR)
    response = requests.get(chain_addr)
    if response.status_code == 200:
        BCChat_transac = []
        BCChat_chain = json.loads(response.content)
        
        for block in BCChat_chain['chain']:
            #print(block)
            for transaction in block['transactions']:
                if(block['BID'] != 0):
                    BCChat_transac.append(transaction)
        
        #print(BCChat_transac)
        print(BCChat_chain['chain'])

        global posts
        posts = sorted(BCChat_transac, key=lambda k: k['time'], reverse=True)

    #return 'Hello World'
    
    return render_template('index.html',
                           title='BlockChain Chat',
                           posts=posts,
                           node_address=NODES_ADDR,
                           readable_time=timestamp_to_string)

@app.route('/submit', methods=['POST'])
def submit_transaction():
    author = request.form['author']
    content = request.form['content']
    #rep_flag = request.form['rep_flag']

    post_object = {
        'author': author,
        'content': content,
        'time': time.time(),
    }
    
    post_json = json.dumps(post_object).encode()
    signature = make_signature(post_json)
    transac_pak = {
        'author': author,
        'content': content,
        'time': post_object['time'],
        'signature': signature,
    }
    #print(post_object.__class__)
    #print(transac_pak.__class__)
    
    transac_addr = "{}/add_new_transaction".format(NODES_ADDR)
    
    requests.post(transac_addr,
                 json=transac_pak,
                 headers={'Content-type': 'application/json'})

    return redirect('/')

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

def make_signature(transac):
    private_key = rsa.PrivateKey.load_pkcs1(pri_key.encode())
    signature = rsa.sign(transac, private_key, 'SHA-1')
    # Here we need to translate signature from bytes to str to make it serializable
    sig_str = str(base64.b64encode(signature), encoding='utf-8')
    return sig_str

