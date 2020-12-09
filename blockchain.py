# database storage
import sqlite3, json, time, random
from hashlib import sha256

# ecdsa keygen and signature module
from ecdsa import SigningKey as PrivKey, NIST192p, VerifyingKey as PubKey

# database interactions
from database import *

# paramaters
# userful parameters to mess with
class Params(object):
    MINT_TIME = 13 #in sec
    TX_FEE = 0.05
    STAKE_DURATION = 60 # duration in sec of a stake before it is returned
    CURVE = NIST192p # ecdsa algorithm curve
    USERCOUNT = 100 # number of default starting compusers
    MAXUSERS = 150 # maximimum number of compusers
    VRATIO = 5 # target ratio of total accounts to validators in our simulation
    MINSTAKED = 100 # minimum number of staked 112Coin for a healthy market
    MIN_TXS = 3 # per timerFired
    MAX_TXS = 8 # per timerFired
    MAX_AMT = 100 # max tx amount one can send
    MIN_AMT = 0.01 # minimum denomination, (1 kos)
    A, B = 2, 0.3 # alpha and beta values for our gamma distribution of tx amts 
    BADSIG_CHANCE = 0.05 # chance of a randomly generated tx having a bad signature
    CHEAT_CHANCE = 0.025 # chance of a minter adding their own txs or validating bad ones
    GENUSER_CHANCE = 0.08 # chance of randomly adding a compuser to the app model

# returns hash of the concatination of the two inputs when they are hashed
def hash2(a, b):
    ahash = sha256(a).hexdigest()
    bhash = sha256(b).hexdigest()
    concat = ahash+bhash
    return sha256(concat.encode()).hexdigest()

#################################################################
#                  OBJECT CREATION FROM JSON
#################################################################

# returns the blockchain object containing all the data about blocks in the chain database
def loadChain():
    blockList = fetchChain()
    genesis = blockList[0]
    # our genesis block
    B = BlockChain(genesis)

    # add the rest of our blocks
    for block in blockList[1:]:
        B.addBlock(block, init=True) # we are initializing, so don't insert block into database again
    return B

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

def loadHumanUsers():
    users = []
    for userTxt in fetchHumanUsers():
        d = json.loads(userTxt[0])
        userObj = User.userFromJSON(d)
        users.append(userObj)
    return users

def loadCompUsers():
    users = []
    for userTxt in fetchCompUsers():
        d = json.loads(userTxt[0])
        userObj = User.userFromJSON(d)
        users.append(userObj)
    return users



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

    @staticmethod
    def txFromJSON(d):
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
    @staticmethod
    def txListDeserializer(L):
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
    @staticmethod
    def serializedTxsList(L):
        txsJSON = []
        for tx in L:
            txJSON = tx.txSerialize()
            txsJSON.append(txJSON)
        return txsJSON

# User object can generate keypairs, verify transaction agianst signature, and sign a transaction
class User(object):
    def __init__(self, fromValues=False, values=None):
        if fromValues: # creating object from User.userFromJSON
            self.pubk, self.privk = values
        else:
            self.pubk, self.privk = User.keyGen() # these are stored as ecdsa module key objects
        self.rawString = self.userSerialize()

    # Key generation and verification code from example at https://pypi.org/project/ecdsa/ 
    @staticmethod
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
        try:
            sig = bytearray.fromhex(sig)
            pubk = bytearray.fromhex(pubk)
            key = PubKey.from_string(pubk, curve=Params.CURVE) # ecdsa key PubKey object
            return key.verify(sig, msg.encode()) # key.verify takes in sig as bytearray, msg as bytes object of string
        except: # this means either signature was not a hexadecimal or it was in hex, but still invalid
            return False
        
    # returns transaction object with user as sender
    def send(self, receiver, amt): # receiver is a hex string of their ecdsa pubkey object to_string() compression format
        date = time.time()
        return Tx(self, receiver, amt, date)

    def userSerialize(self):
        pubkeyString = self.pubk.to_string().hex()
        privkeyString = self.privk.to_string().hex()
        self.rawPubk, self.rawPrivk = pubkeyString, privkeyString
        d = {'Pubkey':pubkeyString, 'Privkey':privkeyString}
        return json.dumps(d)

    @staticmethod
    def userFromJSON(d):
        pubkeyString = d['Pubkey']
        privkeyString = d['Privkey']
        pubk = PubKey.from_string(bytearray.fromhex(pubkeyString), curve=Params.CURVE)
        privk = PrivKey.from_string(bytearray.fromhex(privkeyString), curve=Params.CURVE)
        return User(fromValues=True, values=(pubk, privk))

    # returns a transaction from the coinbase to a user, with receiver input as a hex string of their pubk
    @staticmethod
    def userReward(receiver, randomAmt=True, amount=None):
        sender = 'coinbase'
        amt = round(random.uniform(0.5,10), 2) #smallest unit of currency is a kos or 0.01 112C
        if not randomAmt:
            amt = amount
        date = time.time()
        Hash = Tx.msgHash(sender, receiver, amt, date)
        tx = Tx(None, receiver, amt, date, fromValues=True, values=(sender, None, Hash))
        return tx

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
            self.merkleRoot = Block.merkle(Block.hashList(self.txs))
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

    # recursive 'merging' framework for algorithm from CMU-112 Recursive Merge sort example
    # returns the hash of the root of the merkle tree of transactions
    # takes in a list of hashes of each transaction
    @staticmethod
    def merkle(L):
        newHashes = []
        #base case if no transactions are given, return hash of empty string
        if L == []:
            return sha256(b'').hexdigest()

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
    
    # returns only the valid txs that contain correct signatures and where sender has sufficient funds
    # for the given BlockChain object
    def validTxs(txs, chain):
        if txs == []:
            return []
        result = []
        for txIndex in range(len(txs)):
            tx = txs[txIndex]
            if chain.validSignature(tx) and chain.sufficientBalance(txs, txIndex):
                result.append(tx)
        return result
    
    # returns list of hexcode hashes of all transactions in given list
    @staticmethod
    def hashList(txs):
        hashes = []
        for tx in txs:
            hashes.append(tx.hash)
        return hashes
    
    # TODO implement dynamic Tx Fees that are optional to pay, but this increases chance a tx will not be validated
    # sums the fees from all of the txs 
    @staticmethod
    def totalReward(txs):
        return round(len(txs)*Params.TX_FEE, 2)

# Stores block objects, can add blocks to database, fetch certain blocks from database, and store pertinent info
class BlockChain(object):
    def __init__(self, genesis):
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
    def addBlock(self, block, init=False):
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

        # also add block to blocks table of chain.db so we can load it next time
        # only add if we are not building the initial chain in loadChain()
        if not init:
            insertBlock(block)
    
    # updates the balance of each minter and user in their respective dictionaries
    # def updateBalances(self, block): (NOTE might be better to only verify balance of one user at a time when they spend coin )
        

    # we randomally select a winner from weighted distribution of validators (based on their current stake)
    def lottery(self):
        # create weighted list from validators and stakes
        print("Choosing a Minter...", end='')
        validators = list(self.validators.keys())
        weights = []
        for validator in self.validators:
            weights.append(self.validators[validator][0])
        weightedList = random.choices(validators, weights)
        minter = random.choice(weightedList)
        return minter

    # verifies the signature of a tx is valid using DSA signature verification algorithm
    @staticmethod
    def validSignature(tx):
        sig = tx.signature
        msg = tx.hash
        pubKey = tx.senderKey # convert hex str to bytes
        return User.verify(sig, msg, pubKey)

    # verifies that the sender in a transaction has the amount of coins they are sending
    def sufficientBalance(self, txs, txIndex):
        # get the balance they have accumilated in this txs list, based on all previous txs
        blockBalance = 0
        tx = txs[txIndex]
        totalTxAmt = tx.amt + Params.TX_FEE
        for prevTx in txs[0:txIndex]: # we assume the txs are in chronological order, so we only check txs at the prior indices
            if (prevTx.senderKey == tx.senderKey):
                blockBalance -= (prevTx.amt + Params.TX_FEE) # account for fee
            if (prevTx.receiver == tx.senderKey):
                blockBalance += prevTx.amt

        prevBalance = self.accounts.get(tx.senderKey, 0) # balance from previous block txs
        currBalance = prevBalance + blockBalance
        if totalTxAmt > currBalance:
            return False
        else:
            return True
    
    # will update the current balances of all users based on txs in this confirmed block
    def updateBalances(self, block):
        for tx in block.txs:
            if tx.receiver != 'coinbase':
                self.accounts[tx.receiver] = round(self.accounts.get(tx.receiver, 0) + tx.amt, 2)
            if tx.senderKey != 'coinbase':
                self.accounts[tx.senderKey] = round(self.accounts.get(tx.senderKey, 0) - (tx.amt + Params.TX_FEE), 2)

    # stake an amount of coins at the time of the function call
    def addStake(self, validator, amt):

        # if they do not have enough coin to stake, or already have a stake, then we do nothing
        if (amt > self.accounts.get(validator, 0)):
            return "Insufficient Balance!"
        elif (validator in self.validators):
            return "Already Staked!"
        else:
            self.validators[validator] = (amt, time.time()) 
            
            # remove coin from account balance
            self.accounts[validator] = round(self.accounts[validator] - amt, 2)
            self.staked = round(self.staked + amt, 2)
            return f"Staked {amt} 112C!"
    
    def removeStake(self, validator):
        amt = self.validators[validator][0]
        self.staked = round(self.staked - amt, 2)
        self.validators.pop(validator)
        
        # add coin back to account balance as spendable
        self.accounts[validator] = round(self.accounts[validator] + amt, 2)
    
    # take all of the given transactions and create a block with only valid txs with the given minter
    def mint(self, txs, minter):
        # try:
        # get list of validTxs
        validTxs = Block.validTxs(txs, self)

        # reward calculation and Tx generation
        reward = round(Block.totalReward(validTxs), 2)
        rewardTx = User.userReward(minter, randomAmt=False, amount=reward)
        validTxs.insert(0, rewardTx) # insert reward Tx at the front

        # block creation and adding
        prevHash = self.blocks[-1].hash
        block = Block(validTxs, prevHash, minter)
        return block

        # except Exception as error:
        #     print(error)
        #     print("Mint Failed!") # TODO fix error when non-hexidecimal signature is given for a tx

    # cheatMint creates a 'bad block' in one of four randomly picked ways
    def cheatMint(self, txs, minter):
        cheatType = random.randint(1,4)
        if cheatType == 1: # don't worry about validating txs
            blockTxs = txs
            # reward calculation and Tx generation
            reward = round(Block.totalReward(blockTxs), 2)
            rewardTx = User.userReward(minter, randomAmt=False, amount=reward)
            blockTxs.insert(0, rewardTx) # insert reward Tx at the front
            prevHash = self.blocks[-1].hash


        elif cheatType == 2: # minter gives themselves a massive coinbase mint reward
            # cheat reward Tx generation
            blockTxs = Block.validTxs(txs, self)
            rewardTx = User.userReward(minter, randomAmt=False, amount=1000)
            blockTxs.insert(0, rewardTx) # insert cheat reward Tx at the front
            prevHash = self.blocks[-1].hash

        elif cheatType == 3: # minter adds an extra fake transaction at the end from human user to themselves
            blockTxs = Block.validTxs(txs, self)
            # reward calculation and Tx generation
            reward = round(Block.totalReward(blockTxs), 2)
            rewardTx = User.userReward(minter, randomAmt=False, amount=reward)
            blockTxs.insert(0, rewardTx) # insert reward Tx at the front

            # fake transaction from human
            human = loadHumanUsers()[0]
            stealTx = human.send(minter, 1000)
            blockTxs.append(stealTx)
            prevHash = self.blocks[-1].hash

        elif cheatType == 4: # everything looks good, except the previous hash
            # get list of validTxs
            blockTxs = Block.validTxs(txs, self)

            # reward calculation and Tx generation
            reward = round(Block.totalReward(blockTxs), 2)
            rewardTx = User.userReward(minter, randomAmt=False, amount=reward)
            blockTxs.insert(0, rewardTx) # insert reward Tx at the front
            prevHash = "theyWillNeverSuspectThisOne!"
        # block creation and adding
        block = Block(blockTxs, prevHash, minter)
        return block

    # remove all stakes and give coin back to validator when their stake time is up
    def updateStakes(self):
        validatorsCopy = dict(self.validators) # copy so we don't change the iteratation bounds
        for validator in validatorsCopy:
            startTime = self.validators[validator][1]
            # this user's stake is up, so remove their stake
            if time.time() > (startTime + Params.STAKE_DURATION):
                self.removeStake(validator)

def compUsers():
    users = []
    # create user objects list
    for i in range(Params.USERCOUNT):
        users.append(User())
    return users
