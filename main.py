# Alexander Penney 2020 

import sqlite3
import time, random, linecache
from dataclasses import make_dataclass
from cmu_112_graphics import *

from sqliteDemo import *
#create database in memory
database = sqlite3.connect('test.db')

# so we dont have global vars
class DefaultParams(object):
    MINT_TIME = 13 #in sec
    MAX_TXS = 100
    TX_FEE = 0.01
    
class Block(object):
    def __init__(self, height, txs, time, prevHash, minter): #takes in txs as list containing tuples of transactions in this block
        self.height = height
        self.txs = txs
        self.time = time.asctime(time.localtime(time.time()))
        self.txsHash = self.getHash()
        self.prevHash = prevHash
        self.minter = minter

    def __repr__(self):
        return (f'Block: {self.height}, Txs: {self.txsHash} -- {self.time}')

    # returns the hask of the root of the hash merkle tree of transactions
    def merkleHash(self):
        # TODO implement merkle tree hashing algorithm
        pass

    #hash all the data of this block to send to the next block
    def getHash(self):
        return myHash(self.merkleHash()+myHash(self.time)+myHash(self.prevHash)+myHash(self.height))
    
    #returns the list of txs that contain correct signatures and where sender has sufficient funds
    def validate(self):
        result = []
        for tx in self.txs:
            if validSignature(tx) and sufficientBalance(tx):
                result.append(tx)
        return result

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

    @staticmethod
    

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

runApp(width=700, height=500)