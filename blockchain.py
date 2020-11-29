# sql Functions
from sqlcalls import *

import time, random, linecache
from hashlib import sha256

def formatTime():
    return time.asctime(time.localtime(time.time())) 


# so we dont have global vars
class DefaultParams(object):
    MINT_TIME = 13 #in sec
    MAX_TXS = 100
    TX_FEE = 0.01

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

class Tx(object):
    def __init__(self, sender, receiver, amt, date, signature):
        self.sender = sender
        self.receiver = receiver
        self.amt = amt
        self.date = date
        self.signature = signature
        self.hash = sha256(str(self).encode()).hexdigest()
    
    def __repr__(self):
        return f"{self.sender} to {self.receiver}: {self.amt} -- {self.date}"
    
    @classmethod
    def txFromJSON(cls, d):
        body = d['body']
        sender = body['Sender']
        date = body['Time Stamp']
        receiver = body['Receiver']
        signature = body['Signature']
        amount = body['Amount']
        return Tx(sender, receiver, amount, date, signature)

    # takes in list of JSON rawString txs and returns list of Tx objects
    @classmethod
    def txListDeserializer(cls, L):
        txs = []
        for rawTx in L:
            d = json.loads(rawTx)
            tx = Tx.txFromJSON(d)
            txs.append(tx)
        return txs

        # turns Tx object into json string
    def txSerialize(self):
        d = {}
        d['body'] = {'Sender': self.sender, 
                    'Time Stamp': self.date, 'Receiver': self.receiver, 
                    'Signature': self.signature, 'Amount': self.amt}
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

class Block(object):
    #takes in txs as list of transactions in this block
    def __init__(self, txs, prevHash, minter, currTime=formatTime(), fromValues=False, values=None): 

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
    def validSignature(tx):
        pass

    # verifies that the sender in a transaction has the amount of coins they are sending
    def sufficientBalance(self, block, tx):

        # get the balance they have accumilated in this block, based on all previous txs
        blockBalance = 0
        for prevTx in block.txs:
            if (prevTx.date < tx.date):
                if (prevTx.sender == tx.sender):
                    blockBalance -= prevTx.amt
                if (prevTx.receiver == tx.sender):
                    blockBalance += prevTx.amt

        currBalance = self.accounts[tx.sender] + blockBalance
        if tx.amt > currBalance:
            return False
        else:
            return True
    
    # will update the current balances of all users based on txs in this confirmed block
    def updateBalances(self, block):
        for tx in block.txs:
            self.accounts[tx.sender] = self.accounts.get(tx.sender, 0) - tx.amt
            self.accounts[tx.receiver] = self.accounts.get(tx.receiver, 0) + tx.amt

    @staticmethod
    # creates a genesis block with specified list of txs
    # TODO make the txs from coinbase 
    def createGenesis():
        minter = 'Alby'
        txs = testTxs2()
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

# update our database with a new block
def updateDB(block):
    pass

def testTxs1():
    tx1 = Tx("joe", "mary", 10, time.time(), "h")
    tx2 = Tx("bob", "mary", 10, time.time(), "h")
    tx3 = Tx("bill", "mary", 10, time.time(), "h")
    return [tx1, tx2, tx3]

def testTxs2():
    tx1 = Tx("henry", "mary", 10, time.time(), "h")
    tx2 = Tx("billy", "mary", 10, time.time(), "h")
    tx3 = Tx("mary", "bob", 30, time.time(), "h")
    return [tx1, tx2, tx3]

def testMyTxs1():
    tx1 = Tx("Alby", "mary", 10, time.time(), "h")
    tx2 = Tx("billy", "Alby", 10, time.time(), "h")
    tx3 = Tx("coinbase", "bob", 30, time.time(), "h")
    return [tx1, tx2, tx3]

def testMyTxs2():
    txs = []
    lines = 237 #number of lines in our username file
    for i in range(100):
        #make sure receiver is not same as sender
        while True:
            user = linecache.getline('usernames.txt', random.randint(1,lines))
            if user != 'Alby': break
        amt = random.randint(0,20)
        if random.randint(0,1) == 1:
            tx = Tx(user, "Alby", amt, time.time(), "eyy")
        else:
            tx = Tx('Alby', user, amt, time.time(), "eyy")
        txs.append(tx)
    return txs

def testValidators():
    L = [(f'billy{i}',random.randint(1,50), i) for i in range(30)] + [('alby', 1000, 1)]
    d = {}
    for name, stake, time in L:
        d[name] = (stake, time)
    return d

def testBlocks():
    b = Block(testTxs1(), 0, 'Alby')
    b2 = Block(testTxs2(), b.hash, 'Alby')
    b3 = Block(testMyTxs2(), b2.hash, 'Alby')
    b4 = Block(testMyTxs1(), b3.hash, 'Alby')
    return [b,b2,b3,b4]

# B = BlockChain()
# B.validators = testValidators()
# insertBlock(b)