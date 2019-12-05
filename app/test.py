import pymongo
import json
import time
import rsa
import base64

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.test
collec_User = db.User
collec_BC = db.BlockChain

(pub_key, pri_key) = rsa.newkeys(512)

#print(pub_key.__class__)
#print(pub_key)


user = {
    'name': 'ReallyMonkey',
    'passworld':'1111',
    'public': pub_key.save_pkcs1().decode(),
    'private': pri_key.save_pkcs1().decode(),
}

#collec_User.insert_one(user)
print(user['name'])
'''
new_usr = collec_User.find_one({'name':'ReallyMonkey'})
print(new_usr)

public_key = rsa.PublicKey.load_pkcs1(new_usr['public'].encode())
private_key = rsa.PrivateKey.load_pkcs1(new_usr['private'].encode())

#block = collec_BC.find_one({'BID':1})
#message_o = block['transac']
message = 'asdfasdf'

print(message)
signature = rsa.sign(message.encode(), private_key, 'SHA-1')
print(signature.__class__)

sig = base64.b64encode(signature)
sig_str = str(sig, encoding='utf-8')
print(sig_str.__class__)

#sig_str = signature.decode()
print(rsa.verify(message.encode(), signature, public_key))
try:
    rsa.verify(message.encode(), signature, public_key)
    #ress = rsa.verify(mes.encode(), signature, public_key)
except rsa.pkcs1.VerificationError:
    print('OMG')
else:
    print('true')


#with open('pub_key.pem','w+') as f:
 #   f.write(pub_key.save_pkcs1().decode())
'''