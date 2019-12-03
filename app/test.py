import pymongo
import json
import time

class Block:
    def __init__(self, BID, transaction):
        self.BID = BID
        self.transaction = transaction
        self.time = time.time()

client = pymongo.MongoClient(host='localhost', port=27017)

db = client.test

collection = db.BlockChain

trans = json.dumps({'name':'RM','age':3})
blk = Block(0, trans)

Block1 = {
    'BID': blk.BID,
    'transaction': blk.transaction,
    'time' :blk.time
}

result = collection.insert(Block1)
print(result)
