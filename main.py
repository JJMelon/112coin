# Alexander Penney 2020 

import sqlite3, json
import time, random, linecache
from dataclasses import make_dataclass
from cmu_112_graphics import *
from hashlib import sha256

# keyPress and mousePress handlers:
from handlers import *

# page drawers
from draw import *

# blockchain functions
from blockchain import *

''' --- page number guide --- 
       0: Tutorial
       1: Overview
       2: Send
       3: Mint
       4: Recent
       5: View BlockChain'''

# we try to load the database data, if it's not available we create the database and tables
def loadDatabaseData(app):
    try:
        app.humanUsers = fetchHumanUsers()
        app.currUser = app.humanUsers[0]
        app.compUsers = fetchCompUsers()
        app.chain = loadChain()
        initHumanUserTxsList(app)
    except: # no database created yet, we make the chain.db file and the necessary tables
        makeTable('compusers', blocks=False)
        makeTable('humnausers', blocks=False)
        makeTable('blocks')
        app.humanUsers = [User()]
        app.currUser = app.humanUsers[0]
        app.compUsers = compUsers()
        app.userAddress = app.currUser.rawPubk
        genesis = populateBalances(app) # create initial block giving money to users from coinbase
        app.chain = BlockChain(genesis)
        insertBlock(app.chain.blocks[0])
        app.humanUserTxs = {app.userAddress:myTxs(app, app.currUser)} # stores the tx lists for each human user, so we can quickly load them when switching users

# give each user in app.compUsers a random amount of starting money by creating transactions from the coinbase
# returns a genesis block with these transactions
def populateBalances(app):
    txs = []
    for user in app.compUsers: # get users to give them each a starting amt
        tx = userReward(user)
        txs.append(tx)
    
    # reward original humanuser is 10 112C
    txs.append(userReward(app.currUser, randomAmt=False, amount=10))
    block = Block(txs, None, 'God') # create our genesis block
    return block

# returns a transaction from the coinbase to a user
# TODO FIX human user getting random amount instead of 10 112coin when first startup
def userReward(user, randomAmt=True, amount=None):
    receiver = user.rawPubk
    sender = 'coinbase'
    amt = round(random.uniform(0.5,10), 2) #smallest unit of currency is a kos or 0.01 112C
    if not randomAmt:
        amt = amount
    date = time.time()
    Hash = Tx.msgHash(sender, receiver, amt, date)
    tx = Tx(None, receiver, amt, date, fromValues=True, values=(None, None, Hash))
    return tx

# initializes dict of txs lists for each user in app.humanUsers
def initHumanUserTxsList(app):
    usersTxs = {}
    for user in app.humanUsers:
        name = user.rawPubk
        txs = myTxs(app, user)
        usersTxs[name] = txs
    app.humanUserTxs = usersTxs

# returns list of txs from the chain that involve given user
def myTxs(app, user):
    address = user.rawPubk
    txs = []
    for block in app.chain.blocks:
        for tx in block.txs:
            if tx.senderKey == address or tx.receiver == address:
                txs.append(tx)
    return txs

def appStarted(app):
    app.txWidth = 15
    app.topMargin = 60
    app.sideMargin = 20
    app.page = 0
    app.pages = ['Tutorial', 'Overview', 'Send', 'Mint', 'Recent', 'View Chain']
    # list of pending transactions in memory
    app.pendingTxs = []
    loadDatabaseData(app)
    # initialize recent page details
    app.index = 0 # starting index in app.myTxs, will show this tx and following 9 txs
    app.txWidth = 10 # number of transactions viewable at a time 
    app.topPad = 20
    resetRecentPage(app)

    # initialize block chain viewing page details
    app.blockWidth = 3
    app.currBlocks = app.chain.blocks[0:app.blockWidth]
    app.blockIndex = 0 # which index in the app.blocks list is first in the view list
    app.blockDrawSize = (app.width-4*app.sideMargin)/3
    resetViewPage(app)
    # initIndex(app)
    # populate(app, 1000)

def resetViewPage(app):
    app.index = 0
    app.viewingBlockTxs = False
    app.blockTxsIndex = 0 # index of which block in the 3 app.currBlocks is currently selected to show its transactions 
    currBlockTxs = app.currBlocks[app.blockTxsIndex].txs # currently viewable transactions
    maxViewable = min(app.txWidth, len(currBlockTxs))
    app.currTxs = currBlockTxs[:maxViewable]

def resetRecentPage(app):
    app.index = 0
    currUserTxs = app.humanUserTxs[app.userAddress]
    maxRecentViewable = min(app.txWidth, len(currUserTxs))
    app.currTxs = currUserTxs[0:maxRecentViewable] # currently viewable transactions

def timerFired(app):
    app.timerDelay = 250

def pageHandler(app, event):
    if event.key == "Right":
        app.page += 1
        if app.page > 5:
            app.page = 0
        return True
    if event.key == "Left":
        app.page -= 1
        if app.page < 0:
            app.page = 5
        return True

def keyPressed(app, event):
    if pageHandler(app, event):
        return
    elif app.page == 0:
        tutorialKeyHandler(app, event)
    elif app.page == 1:
        overviewKeyHandler(app, event)
    elif app.page == 2:
        sendKeyHandler(app, event)
    elif app.page == 3:
        mintKeyHandler(app, event)
    elif app.page == 4:
        recentKeyHandler(app, event)
    elif app.page == 5:
        viewKeyHandler(app, event)

def mousePressed(app, event):
    navBarClickHandler(app, event)
    if app.page == 0:
        tutorialClickHandler(app, event)
    elif app.page == 1:
        overviewClickHandler(app, event)
    elif app.page == 2:
        sendClickHandler(app, event)
    elif app.page == 3:
        mintClickHandler(app, event)
    elif app.page == 4:
        recentClickHandler(app, event)
    elif app.page == 5:
        viewClickHandler(app, event)

def redrawAll(app, canvas):
    drawNavbar(app, canvas)
    if app.page == 0:
        drawTutorial(app, canvas)
    elif app.page == 1:
        drawOverview(app, canvas)
    elif app.page == 2:
        drawSend(app, canvas)
    elif app.page == 3:
        drawMint(app, canvas)
    elif app.page == 4:
        drawRecent(app, canvas)
    elif app.page == 5:
        drawView(app, canvas)

# makeInitialTable()
runApp(width=700, height=500)