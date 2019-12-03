import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

NODES_ADDR = "http://localhost:8000"
posts = []

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
        #'rep_flap': rep_flag,
    }

    transac_addr = "{}/add_new_transaction".format(NODES_ADDR)

    requests.post(transac_addr,
                 json=post_object,
                 headers={'Content-type': 'application/json'})

    return redirect('/')

def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

