# database storage
import sqlite3, json

import time, random, linecache
from hashlib import sha256

# ecdsa keygen and signature module
from ecdsa import SigningKey as PrivKey, NIST192p, VerifyingKey as PubKey

# so we dont have global vars
class Params(object):
    MINT_TIME = 13 #in sec
    MAX_TXS = 100
    TX_FEE = 0.01
    CURVE = NIST192p

# returns hash of the concatination of the two inputs when they are hashed
def hash2(a, b):
    ahash = sha256(a).hexdigest()
    bhash = sha256(b).hexdigest()
    concat = ahash+bhash
    return sha256(concat.encode()).hexdigest()

# returns the blockchain object containing all the data about blocks in the chain database
def loadChain():
    B = BlockChain()
    blockList = fetchChain()
    # replace first default genesis block with correct block
    B.blocks[0] = blockList[0]
    for block in blockList[1:]:
        B.addBlock(block)
    return B


# Tx objects are created by a User object by default, but can be created from values when deserializing
class Tx(object):
    def __init__(self, senderObj, receiver, amt, date, fromValues=False, values=None):
        # takes in sender as User object when signing
        self.receiver = receiver # hex str of receivers's public ecdsa key 
        self.amt = amt
        self.date = date
        if fromValues: # creating Tx from deserialized Dictionary w/ values = (senderKey, signature, hash)
            self.senderKey, self.signature, self.hash = values
        else: # creating Tx when calling user.send()
            self.senderKey = senderObj.pubk.to_string().hex()
            self.hash = Tx.msgHash(self.senderKey, self.receiver, self.amt, self.date)
            self.signature = senderObj.sign(self.hash)
    
    def __repr__(self):
        return f"{self.senderKey} to {self.receiver}: {self.amt} -- {self.date}"
    
    @staticmethod
    def msgHash(sender, receiver, amt, date):
        string = str(sender) + str(receiver) + str(amt) + str(date)
        return sha256(string.encode()).hexdigest()

    @classmethod
    def txFromJSON(cls, d):
        body = d['body']
        sender = body['Sender'] # hex string
        date = body['Time Stamp']
        receiver = body['Receiver'] # hex string
        signature = d['Signature'] #data is a hex string
        amount = body['Amount']
        Hash = d['id']
        Values = sender, signature, Hash
        # None as first param because we dont have a sender Object
        return Tx(None, receiver, amount, date, fromValues=True, values=Values)

    # takes in list of JSON rawString txs and returns list of Tx objects
    @classmethod
    def txListDeserializer(cls, L):
        txs = []
        for rawTx in L:
            d = json.loads(rawTx)
            tx = Tx.txFromJSON(d)
            txs.append(tx)
        return txs

        # turns Tx object into json string, with option of not including a specified signature for reuse in signing
    def txSerialize(self, includeSig=True):
        d = {}
        d['body'] = {'Sender': self.senderKey, 'Time Stamp': self.date, 
        'Receiver': self.receiver, 'Amount': self.amt}
        if includeSig:
            d['Signature'] = self.signature
        d['id'] = self.hash
        return json.dumps(d)

    # takes in list of Tx objects and returns list of serialized JSON rawStrings
    @classmethod
    def serializedTxsList(cls, L):
        txsJSON = []
        for tx in L:
            txJSON = tx.txSerialize()
            txsJSON.append(txJSON)
        return txsJSON

# User object can generate keypairs, verify transaction agianst signature, and sign a transaction
class User(object):
    def __init__(self):
        self.pubk, self.privk = User.keyGen()
    
    @staticmethod
    # Key generation and verification code from example at https://pypi.org/project/ecdsa/ 
    def keyGen():
        privk = PrivKey.generate()
        pubk = privk.verifying_key
        return (pubk, privk) # returns keys as ecdsa module key objects
    
    # returns bytes signature of msg using the user objects private key
    def sign(self, msg):
        return self.privk.sign(msg.encode()).hex()
    
    # returns True if signature is correct for given message and public key, sig as hex object
    @staticmethod
    def verify(sig, msg, pubk): # takes pubk, sig, msg as strings
        sig = bytearray.fromhex(sig)
        pubk = bytearray.fromhex(pubk)
        key = PubKey.from_string(pubk, curve=Params.CURVE) # ecdsa key PubKey object
        return key.verify(sig, msg.encode()) # key.verify takes in sig as bytearray, msg as bytes object of string

    # returns transaction object with user as sender
    def send(self, receiver, amt): # receiver is a hex string of their ecdsa pubkey object to_string() compression format
        date = time.time()
        return Tx(self, receiver, amt, date)


class Block(object):
    #takes in txs as list of transactions in this block
    def __init__(self, txs, prevHash, minter, currTime=time.time(), fromValues=False, values=None): 

        #always pass in when building
        self.txs = txs
        self.rawTxsList = Tx.serializedTxsList(self.txs)
        self.prevHash = prevHash
        self.minter = minter

        # when building from values, we input the hash, merkleRoot for efficiency/accuracy and also correct time
        if fromValues:
           self.merkleRoot, self.hash, self.time = values
        else:
            self.time = currTime 
            self.merkleRoot = Block.merkle(self.hashList())
            self.hash = self.getHash()

        self.rawString = self.blockSerialize(incHash=True)

    def blockSerialize(self, incHash=False):
        d = {}
        d['header'] = {'Time Stamp': self.time, 'Previous Hash': self.prevHash, 
                    'Minter': self.minter, 'merkleRoot': self.merkleRoot}
        if incHash:
            d['header'].update({'Hash': self.hash})
        d['transactions'] = self.rawTxsList
        return json.dumps(d)
    
    def __repr__(self):
        return (f'[Block Hash: {self.hash} -- {self.time}]')

    @staticmethod
    # returns the hash of the root of the merkle tree of transactions
    # tales in a list of hashes of each transaction
    def merkle(L):
        newHashes = []
        #base case if no transactions are given, return hash of empty string
        if L == []:
            return sha256('').hexdigest()

        # base case when length list is 1, we have our root
        elif len(L) == 1:
            return L[0]

        # group each two elements and create hashlist of newHashes
        else:
            # accounts for an odd number of el'ts, duplicating last hash
            if len(L)%2 == 1:
                L.append(L[-1])
            for i in range(0, len(L)-1, 2):
                hashA, hashB = L[i], L[i+1]
                newHash = hash2(hashA.encode(), hashB.encode())
                newHashes.append(newHash)
        return Block.merkle(newHashes)

    @classmethod
    def blockFromJSON(cls, d):
        header = d['header']
        time = header['Time Stamp']
        prevHash = header['Previous Hash']
        minter = header['Minter']
        merkleRoot = header['merkleRoot']
        Hash = header['Hash']
        rawTxsList = d['transactions']
        txs = Tx.txListDeserializer(rawTxsList)
        inputValues = (merkleRoot, Hash, time)
        return Block(txs, prevHash, minter, fromValues=True, values=inputValues)

    #hash all the data of this block to send to the next block
    def getHash(self):
        return sha256(json.dumps(self.blockSerialize()).encode()).hexdigest()
    
    #returns the list of txs that contain correct signatures and where sender has sufficient funds
    def validTxs(self):
        result = []
        for tx in self.txs:
            if BlockChain.validSignature(tx) and BlockChain.sufficientBalance(tx):
                result.append(tx)
        return result
    
    # returns list of hexcode hashes of all transactions in this block
    def hashList(self):
        hashes = []
        for tx in self.txs:
            hashes.append(tx.hash)
        return hashes

# blockChain object does not directly store the whole chain, would be too big for memory.
# instead we use it to add blocks to database, fetch certain blocks from database, and store pertinent info
class BlockChain(object):
    def __init__(self):
        genesis = BlockChain.createGenesis()
        self.blocks = [genesis]
        # have dictionary of accounts by their address and their current balances
        self.accounts = {}
        self.updateBalances(genesis)
        # dictionary of (validator address: (amt staked, return time)
        self.validators = {}

        # total amount staked is linked to self.validators
        self.staked = 0

        # possibly implement other forks in a BlockChain, maybe 2D list?

    # once block is minted, it *should* be validated correctly and we can update balances from the block txs
    def addBlock(self, block):
        if (block.prevHash != self.blocks[-1].hash):
            cont = input("This block has an incorrect Previous Hash\nAre you sure you want to continue? ")
            if cont.upper() == "Y":
                print("Block Added!")
            else:
                print("Block Add Aborted!")
                return
        # update balance of users 
        self.updateBalances(block)

        self.blocks.append(block)
    
    # updates the balance of each minter and user in their respective dictionaries
    # def updateBalances(self, block): (NOTE might be better to only verify balance of one user at a time when they spend coin )
        

    # we randomally select a winner from weighted distribution of validators (based on their current stake)
    def lottery(self):
        # create weighted list from validators and stakes
         validators = list(self.validators.keys())
         weights = []
         for validator in self.validators:
             weights.append(self.validators[validator][0])
         weightedList = random.choices(validators, weights)
         return random.choice(weightedList)

    # verifies the signature of a tx is valid using DSA signature verification algorithm
    @staticmethod
    def validSignature(tx):
        sig = tx.signature
        msg = tx.hash
        pubKey = tx.senderKey # convert hex str to bytes
        return User.verify(sig, msg, pubKey)

    # verifies that the sender in a transaction has the amount of coins they are sending
    def sufficientBalance(self, block, tx):
        # get the balance they have accumilated in this block, based on all previous txs
        blockBalance = 0
        for prevTx in block.txs:
            if (prevTx.date < tx.date):
                if (prevTx.senderKey == tx.senderKey):
                    blockBalance -= prevTx.amt
                if (prevTx.receiver == tx.senderKey):
                    blockBalance += prevTx.amt

        currBalance = self.accounts[tx.senderKey] + blockBalance
        if tx.amt > currBalance:
            return False
        else:
            return True
    
    # will update the current balances of all users based on txs in this confirmed block
    def updateBalances(self, block):
        for tx in block.txs:
            self.accounts[tx.senderKey] = self.accounts.get(tx.senderKey, 0) - tx.amt
            self.accounts[tx.receiver] = self.accounts.get(tx.receiver, 0) + tx.amt

    @staticmethod
    # creates a genesis block with specified list of txs
    # TODO make the txs from coinbase 
    def createGenesis():
        minter = 'Alby'
        txs = testUserObjTxs()
        return Block(txs, time.time(), None, minter)

    # stake an amount of coins at the time of the function call
    def addStake(self, validator, amt):
        if amt > self.accounts[validator]:
            print("Stake too high!")
            return
        self.validators[validator] = self.validators.get(validator, 0) + amt
        self.staked += amt
    
    def removeStake(self, validator):
        self.staked -= self.validators[validator]
        self.validators.remove(validator)

def testMyTxs(user):
    usersObjs = []
    txs = []
    # create user objects list
    for i in range(10):
        usersObjs.append(User())

    # 10 random txs involving app.user, either send or receive
    for i in range(20):
        send = random.randint(0,1)
        amt = random.randint(0,20)
        if send:
            receiver = random.choice(usersObjs).pubk.to_string().hex()
            tx = user.send(receiver, amt)
        else:
            sender = random.choice(usersObjs) # hex representation of compressed user PubKey object
            receiver = user.pubk.to_string().hex()
            tx = sender.send(receiver, amt)
        txs.append(tx)
    return txs

def testUserObjTxs():
    usersObjs = []
    txs = []
    # create user objects list
    for i in range(20):
        usersObjs.append(User())

    # each user sends to a random receiver, not themselves
    for user in usersObjs:
        while True:
            receiver = random.choice(usersObjs).pubk.to_string().hex() # hex representation of compressed user PubKey object
            if receiver != user.pubk.to_string().hex(): break
        amt = random.randint(0,20)
        tx = user.send(receiver, amt)
        txs.append(tx)
    return txs
        
        
def testValidators():
    L = [(f'billy{i}',random.randint(1,50), i) for i in range(30)] + [('alby', 1000, 1)]
    d = {}
    for name, stake, time in L:
        d[name] = (stake, time)
    return d

def testBlocks():
    b = Block(testUserObjTxs(), '0', 'Alby')
    b2 = Block(testUserObjTxs(), b.hash, 'Alby')
    b3 = Block(testUserObjTxs(), b2.hash, 'Alby')
    b4 = Block(testUserObjTxs(), b3.hash, 'Alby')
    return [b,b2,b3,b4]


me = User()


B = BlockChain()
# B.validators = testValidators()
# insertBlock(b)



'''
-------------------SQL DATABASE REFERENCES---------------
chain.db - stores table of blocks 
myTxs.db - stores all of your transactions (might not need if we can reconstruct from the chain)

TABLES:
    chain.db:
        blocks: JSON rawstring of blocks, row id is block height

'''


#create database in memory
database = sqlite3.connect('test.db')

#returns list of n random transactions
def makeTxs(n):
    txs = []
    for tx in range(n):
        txs.append(createTx())
    return txs

def makeTable(name, dbname):
    try:
        database = sqlite3.connect(dbname)
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        query = '''CREATE TABLE %s (
                        id integer primary key autoincrement,
                        block text
                        )''' %name
        c.execute(query)
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print(f"Table {name} Created in {dbname}!")

def sqlTransaction(query, msg='', fetch=False):
    try:
        database = sqlite3.connect('chain.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        c.execute(query)
        result = c.fetchall()
        database.commit()
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print(msg)
        if fetch:
            return result 

#######################################################
#                  BLOCK FUNCTIONS
#######################################################

# returns a list of block objects for all blocks in a db
def fetchChain():
    query = "SELECT * From blocks"
    chain = sqlTransaction(query, fetch=True)
    blocks = []
    for blockValues in chain:
        d = json.loads(blockValues[1])
        block = Block.blockFromJSON(d)
        blocks.append(block)
    return blocks


# returns dictionary representation of the block at specified height
def blockDeserializer(height):
    # we fetch our id from the height+1 because of starting at 1 in the db
    query = "SELECT * FROM blocks WHERE id = %s" %(height+1)
    rawString = sqlTransaction(query, fetch=True)[0][1]
    d = json.loads(rawString)
    return d

def insertBlock(block):
    msg = "Inserted Block into chain.db!"
    query = "INSERT INTO blocks (block) VALUES ('%s')" %block.rawString
    sqlTransaction(query, msg)

#######################################################
#               TRANSACTION FUNCTIONS
#######################################################

# def txsDeserializer()

def getSent(user):
    c.execute("SELECT * FROM txs WHERE sender=?", (user,))
    return c.fetchall()

def getReceived(user):
    c.execute("SELECT * FROM txs WHERE receiver=?", (user,))
    return c.fetchall()

def removeTx(place):
    with database:
        c.execute("DELETE from txs WHERE name=?", (place))

def delTable(table, dbname):
    try:
        database = sqlite3.connect(dbname)
        c = database.cursor()
        query = f'DROP TABLE {table}'
        c.execute(query)
        database.commit()
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("The %s table was Dropped!"%table)

#returns list of txs from starting index to end index inclusive
def getTxsRange(start, end, c):
    c.execute("SELECT * FROM txs WHERE id >= ? AND id <= ?", (start, end))
    return c.fetchall()

#populate the database with n random transactions
def populate(app, n):
    try:
        database = sqlite3.connect('test.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        
        #insert our n # of txs into the database
        for tx in makeTxs(n):
            insertTx(tx, c)

        database.commit() 
        #update our app model with the newly updated database
        c.execute("SELECT * FROM txs")
        app.txs = c.fetchall()
        updateMaxIndex(app, c) 
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("Database closed")

#puts the initial transactions from our db into memory when app is started and
#sets our starting index to 0, assigns current transactions to the first app.txWidth #
def initIndex(app):
    try:
        database = sqlite3.connect('test.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        c.execute("SELECT * FROM txs")

        #app model controller
        app.index = 0
        app.txs = c.fetchall()
        app.currTxs = app.txs[0:app.txWidth]
        updateMaxIndex(app, c)
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("Database closed")