# Alexander Penney 2020 

import sqlite3, json
import time, random, linecache
from dataclasses import make_dataclass
from cmu_112_graphics import *
from hashlib import sha256

from sqliteDemo import *
#create database in memory
database = sqlite3.connect('test.db')
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

class Block(object):
    def __init__(self, height, txs, prevHash, minter): #takes in txs as list containing tuples of transactions in this block
        self.height = height
        self.txs = txs
        self.time = time.asctime(time.localtime(time.time()))
        self.prevHash = prevHash
        self.minter = minter
        self.merkleRoot = Block.merkle(self.hashList())
        self.hash = self.getHash()

    def __repr__(self):
        return (f'Block: {self.height}, Txs: {self.txsHash} -- {self.time}')

    @staticmethod
    # returns the hash of the root of the merkle tree of transactions
    # tales in a list of hashes of each transaction
    def merkle(L):
        newHashes = []
        # base case when length list is 1, we have our root
        if len(L) == 1:
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
        

    #hash all the data of this block to send to the next block
    def getHash(self):
        # return sha256(json.dumps(self).enocde())
    
    #returns the list of txs that contain correct signatures and where sender has sufficient funds
    def validate(self):
        result = []
        for tx in self.txs:
            if validSignature(tx) and sufficientBalance(tx):
                result.append(tx)
        return result
    
    # returns list of hexcode hashes of all transactions in this block
    def hashList(self):
        return [sha256(self.txs[i].encode()).hexdigest() for i in range(len(self.txs))]

class BlockChain(object):
    def __init__(self):
        self.blocks = [Blockchain.createGenesis()]
        # have dictionary validators and their current balances
        self.minters = []
        self.users = []

        # possibly implement other forks in BlockChain, maybe 2D list?

    # once block is minted, it *should* be validated correctly and we can update balances from the block txs
    def addBlock(self, block):
        
        # update balance of minters and users (where minters are actively minting/validating and transacting, users only generate transactions)
        self.updateBalances(block)

        self.blocks.append(block)
    
    # updates the balance of each minter and user in their respective dictionaries
    def updateBalances(self, block):
        pass

    # we randomally select a winner from weighted distribution of validators (based on their current stake)
    def lottery(self):
        pass

    

# creates a genesis block with specified list of txs
# TODO make the txs from coinbase 
def createGenesis(txs, minter):
    return Block(0, txs, time.time(), None, minter)

def appStarted(app):
    app.txWidth = 15
    app.topMargin = 60
    app.sideMargin = 20
    initIndex(app)
    # populate(app, 1000)

def timerFired(app):
    pass

def keyPressed(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "p":
        print('populating...')
        populate(app, app.txWidth)
        dIndex = app.txCount - app.index - app.txWidth
        moveIndex(app, dIndex)
    elif event.key == "s":
        moveIndex(app, -app.index)

def moveIndex(app, dir):
    app.index += dir
    if app.index < 0:
        app.index = 0
    elif app.index > app.txCount - app.txWidth:
        app.index = app.txCount - app.txWidth
    app.currTxs = app.txs[app.index: app.index + app.txWidth]

def redrawAll(app, canvas):
    drawTitle(app, canvas)
    if app.txs != []:
        drawTxs(app, canvas)

def drawTxs(app, canvas):
    txBoxHeight = (app.height-2*app.topMargin)//app.txWidth 
    for i in range(app.txWidth):
        tx = app.currTxs[i]
        x0, y0 = app.sideMargin, app.topMargin + i*txBoxHeight
        drawTx(app, canvas, tx, x0, y0)

def drawTx(app, canvas, tx, x0, y0):
    txBoxHeight = (app.height-2*app.topMargin)//app.txWidth 
    txBoxWidth = app.width - 2*app.sideMargin
    canvas.create_rectangle(x0, y0, x0 + txBoxWidth, y0 + txBoxHeight, width=2)
    txtCy = y0 + txBoxHeight/2
    ID, sender, receiver, amt, time = tx
    canvas.create_text(x0 + app.sideMargin, txtCy, text=(f'{ID}: From: {sender} To: {receiver} -- ${amt} -- %0.3f' %time), 
            font='Arial 10 bold', anchor=W)

# makeInitialTable()

# runApp(width=700, height=500)