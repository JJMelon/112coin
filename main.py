# Alexander Penney 2020 
import time, random, os, json, sqlite3
from hashlib import sha256

from cmu_112_graphics import *
from blockchain import *  # blockchain functions
from handlers import * # keyPress and mousePress handlers:
from draw import * # page drawers

''' --- page number guide --- 
       0: Tutorial
       1: Overview
       2: Send
       3: Mint
       4: Recent
       5: View BlockChain'''

################################################################################
#                           App Initialization
################################################################################

# we try to load the database data, if it's not available we create the database and tables
def loadDatabaseData(app):
    dbExists = os.path.exists('chain.db')
    if dbExists:
        print("Loading data from chain.db...", end='')
        app.humanUsers = loadHumanUsers()
        app.currUser = app.humanUsers[0]
        app.userAddress = app.currUser.rawPubk
        app.compUsers = loadCompUsers()
        app.chain = loadChain()
        initHumanUserTxsList(app)
        print("Done!")
    else:
        print('''
----------------------------------------------------------
                   Welcome to 112Coin! 
              Initializing First Time Setup:
----------------------------------------------------------''')
        # make our database and its tables
        makeTable('compusers', blocks=False)
        makeTable('humanusers', blocks=False)
        makeTable('blocks')

        # update app model
        app.humanUsers = [User()]
        app.currUser = app.humanUsers[0]
        app.compUsers = compUsers() # generate random computer users
        app.userAddress = app.currUser.rawPubk
        genesis = populateBalances(app) # create initial block giving money to users from coinbase
        app.chain = BlockChain(genesis)
        app.humanUserTxs = {app.userAddress:myTxs(app, app.currUser)} # stores the tx lists for each human user, so we can quickly load them when switching users

        # store these generated data in our database 
        print("Initializing Default Data in chain.db...", end='')
        insertBlock(app.chain.blocks[0])
        insertHumanUser(app.currUser)
        for user in app.compUsers:
            insertCompUser(user)
        print('Done!')
        

# give each user in app.compUsers a random amount of starting money by creating transactions from the coinbase
# returns a genesis block with these transactions
def populateBalances(app):
    txs = []
    for user in app.compUsers: # get users to give them each a starting amt
        tx = User.userReward(user.rawPubk)
        txs.append(tx)
    
    # reward original humanuser is 10 112C
    txs.append(User.userReward(app.userAddress, randomAmt=False, amount=10.00))
    block = Block(txs, None, 'God') # create our genesis block
    return block

# initializes dict of txs lists for each user in app.humanUsers
def initHumanUserTxsList(app):
    usersTxs = {}
    for user in app.humanUsers:
        name = user.rawPubk
        txs = myTxs(app, user)
        usersTxs[name] = txs
    app.humanUserTxs = usersTxs

################################################################################
#                          User Simulation
################################################################################

# small chance of adding a new user to compusers, coming in with a starting receive transaction of course
def genUser(app):
    pValue = random.random()
    if len(app.compUsers) >= Params.MAXUSERS:
        return
    if pValue < Params.GENUSER_CHANCE:
        newUser = User()
        sender = random.choice(app.compUsers) # pick a sender
        amt = round(random.uniform(2,5))
        app.compUsers.append(newUser)
        # create transction from a random compuser, like they bought coin for cash from another account
        newTx = sender.send(newUser.rawPubk, amt)
        app.txsPool.append(newTx)
        print(f'New User: {newUser.rawPubk[0:10]}... has joined!')


# adds some random txs to the app.txsPool list, some may be insufficient balance or invalid signature
def generateTxs(app):
    numTxs = random.randint(Params.MIN_TXS, Params.MAX_TXS)
    for i in range(numTxs):
        sender = random.choice(app.compUsers)
        # each user sends to a random receiver, cannot be themselves
        while True:
            receiver = random.choice(app.compUsers).rawPubk # receiver is a hex string
            if receiver != sender.rawPubk: break


        # we need to weight the tx amt towards low end of scale, so use a skewed distribution
        while True:
            # we also need to prevent lots of txs with amounts just barely more than the fee, as this is unrealistic
            amt = round(random.gammavariate(Params.A, Params.B), 2)
            if Params.MIN_AMT < amt < Params.MAX_AMT: break

        # chance of an invalid signature 
        badSigNum = random.random()
        if badSigNum < Params.BADSIG_CHANCE:
            date = time.time()
            Hash = Tx.msgHash(sender.rawPubk, receiver, amt, date)
            sig = 'whyyyyy'.encode().hex() # bad signature
            tx = Tx(None, receiver, amt, date, fromValues=True, values=(sender.rawPubk, sig, Hash))
        else: # create tx using normal Ecdsa signature method
            tx = sender.send(receiver, amt)
        app.txsPool.append(tx)

    txTextL = len(str(numTxs))
    padText = '-'*(3-txTextL)
    print(f'{numTxs} {padText} New Transactions!')
    
    app.currPoolTxs = app.txsPool[app.index: app.index + app.txsPoolWidth]

# initially randomly chooses a quarter of compusers to stake, simulating an active crypto eco-system
def setValidators(app):
    amt = round(random.uniform(0.5, 8), 2)
    pValue = (1 / Params.VRATIO)
    # continue until we have the target amount of validators
    while True:
        user = random.choice(app.compUsers) 
        address = user.rawPubk
        app.chain.addStake(address, amt)
        if len(app.chain.validators) > (Params.USERCOUNT/Params.VRATIO):
            break
    
    topStaker(app) # update stake statistics

# choose some random users to stake, make sure they aren't already staked
def randomStakes(app):
    numStake = random.randint(0,3)
    amt = random.uniform(1,20)
    n = 0
    while n < numStake:
        accounts = list(app.chain.accounts)
        userAddress = random.choice(accounts)
        # case for when every account is a validator, we should just break and wait until some validators are removed
        if len(app.chain.validators) >= (len(accounts)//Params.VRATIO):
            break
        elif (userAddress in app.chain.validators) or (userAddress == app.userAddress):
            pass
        else:
            app.chain.addStake(userAddress, amt)
            n += 1


################################################################################
#                           Top-Level App Funcions
################################################################################


def appStarted(app):
    app.txWidth = 15
    app.topMargin = 60
    app.sideMargin = 20
    app.page = 0
    app.pages = ['Tutorial', 'Overview', 'Send', 'Mint', 'Recent', 'View Chain']
    app.timerDelay = 1000
    app.generating = False # start waiting for user to toggle generating transactions
    app.runningAI = False # wait to start simulation timer
    app.count = 1 # internal timer for validator minting simulation
    loadImages(app)
    loadColors(app)
    # list of pending transactions in memory
    app.txsPool = []
    app.minting = False # used to prevent generating txs during mint process

    # load Human User, Computer User, and Block Data
    loadDatabaseData(app)
    
    # TEST set our initial validators as a random selection of comp users
    setValidators(app)

    # initialize overview page details
    app.stakeDuration = Params.STAKE_DURATION

    # ---------------------------------------
    #       SPECIFIC PAGE DETAILS
    # ---------------------------------------

    # send page 
    resetSendPage(app)

    # initialize recent page details
    app.index = 0 # starting index in app.myTxs, will show this tx and following 9 txs
    app.txWidth = 10 # number of transactions viewable at a time for normal list pages (recent, block view)
    app.topPad = 20
    app.currTxBox = -1
    resetRecentPage(app)

    # initialize block chain viewing page details
    app.blockWidth = 3
    app.currBlocks = app.chain.blocks[0:app.blockWidth]
    app.blockIndex = 0 # which index in the app.blocks list is first in the view list
    app.blockDrawSize = (app.width-4*app.sideMargin)/3
    resetViewPage(app)

    # initialize mint page details
    app.txsPoolWidth = 8
    resetMintPage(app)

    resetTutorialPage(app)
    # initIndex(app)
    # populate(app, 1000)

def resetTutorialPage(app):
    # coords of box for proof of stake info button
    Btn1W, Btn1H = 120, 50
    btn1Y = 220
    btnX = (app.width/2 - Btn1W/2)
    Btn1X0, Btn1Y0 = btnX, app.topMargin + btn1Y
    text1 = '  More about\nProof of Stake'
    app.tutorialButton = (Btn1X0, Btn1Y0, Btn1X0 + Btn1W, Btn1Y0 + Btn1H, text1)
    app.tutorialButtonColor = 'gold'

    Btn1W, Btn1H = 200, 75
    botPad = 25
    Btn1X0, Btn1Y0 = app.width/2 - Btn1W/2, app.height - Btn1H - botPad
    text2 = '  Start the\nSimulation'
    app.startButton = (Btn1X0, Btn1Y0, Btn1X0 + Btn1W, Btn1Y0 + Btn1H, text2)
    app.startButtonColor = 'gold'

def resetViewPage(app):
    app.viewingBlockTxs = False
    app.blockTxsIndex = 0 # index of which block in the 3 app.currBlocks is currently selected to show its transactions 
    currBlockTxs = app.currBlocks[app.blockTxsIndex].txs # currently viewable transactions
    maxViewable = min(app.txWidth, len(currBlockTxs))
    app.currBlockTxs = currBlockTxs[:maxViewable]

def resetRecentPage(app):
    currUserTxs = app.humanUserTxs[app.userAddress]
    maxRecentViewable = min(app.txWidth, len(currUserTxs))
    app.currRecentTxs = currUserTxs[0:maxRecentViewable] # currently viewable transactions

def resetMintPage(app):
    maxPoolViewable = min(app.txsPoolWidth, len(app.txsPool))
    app.currPoolTxs = app.txsPool[0:maxPoolViewable]
    app.currReward = Block.totalReward(app.txsPool)

def resetSendPage(app):
    # coords of box for send button to enter user 
    Btn1W, Btn1H = 75, 50
    btn1Y = 100
    btnX = 40
    Btn1X0, Btn1Y0 = app.sideMargin + btnX, app.topMargin + btn1Y
    text1 = '  Enter\nAddress'
    app.sendButton1 = (Btn1X0, Btn1Y0, Btn1X0 + Btn1W, Btn1Y0 + Btn1H, text1)
    app.sendButton1Color = 'gold'
    # receiver user address field
    app.recAddress = ''

    # coords of box for send button to enter amount
    text2 = '  Enter\nAmount'
    Btn2W, Btn2H = 75, 50
    Btn2X0, Btn2Y0 = app.sideMargin + btnX, Btn1Y0 + Btn1H + 40
    app.sendButton2 = (Btn2X0, Btn2Y0, Btn2X0 + Btn2W, Btn2Y0 + Btn2H, text2)
    app.sendButton2Color = 'gold'
    # amount field
    app.sendAmount = '...'

    # coords of box to confirm the send transaction
    text3 = 'Confirm Transaction'
    Btn3W, Btn3H = 200, 45
    Btn3X0, Btn3Y0 = app.width/2-Btn3W/2, app.height-160
    app.sendButton3 = (Btn3X0, Btn3Y0, Btn3X0 + Btn3W, Btn3Y0 + Btn3H, text3)
    app.sendButton3Color = 'gold'


def loadImages(app):
    app.coinImg = app.loadImage('media/Coin.png')
    app.coinImg = app.scaleImage(app.coinImg, 1/5)
    app.emptyImg = app.loadImage('media/empty.png')
    app.emptyImg = app.scaleImage(app.emptyImg, 7/9)
    app.chainImg = app.loadImage('media/chain.png')
    app.chainImg = app.scaleImage(app.chainImg, 3/10)
    app.sendImg = app.loadImage('media/send.png')
    app.sendImg = app.scaleImage(app.sendImg, 1)

def loadColors(app):
    app.dGold = '#c3ad34'
    app.grey='#7e7e7e'
    app.lGrey = '#f0f0f0'
    app.lGold = '#FFC300'
    app.lGreen = '#7DAA6A'
    app.mGreen = '#438029'

def timerFired(app):
    if app.runningAI:
        topStaker(app)
        app.count += 1
        app.chain.updateStakes()
        randomStakes(app)
        genUser(app)
    if app.count % Params.MINT_TIME == 0: # when we reach mint time
        app.count = 0
        mintBlock(app)
    if (app.generating) and (not app.minting):
        generateTxs(app)
    app.currReward = Block.totalReward(app.txsPool)

def pageHandler(app, event):
    # don't let user interact until the simulation has begun
    if (not app.runningAI):
        app.showMessage('Error', 'Please start the simulation first!')
        return True
    if event.key == "Right":
        app.index = 0
        app.page += 1
        if app.page > 5:
            app.page = 0
        return True
    if event.key == "Left":
        app.index = 0
        app.page -= 1
        if app.page < 0:
            app.page = 5
        return True

def keyPressed(app, event):
    if pageHandler(app, event):
        return

    # TEST DEBUG
    elif event.key == 'g':
        app.generating = not app.generating
        if app.generating: print('Generating toggled ON')
        else: print('Stopped Generating')
    elif event.key == 'm':
        mintBlock(app)

    # END TEST DEBUG
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

def mouseMoved(app, event):
    if app.page == 0:
        tutorialMouseHandler(app, event)
    elif app.page == 2:
        sendMouseHandler(app, event)

def redrawAll(app, canvas):
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
    drawNavbar(app, canvas)


################################################################################
#                       Minting & Validation Functions
################################################################################

# sets the app.topStaker 
def topStaker(app):
    stakes = app.chain.validators
    app.topStaker = max(stakes, key = lambda k: stakes[k][0])
    app.topStake = round(stakes[app.topStaker][0], 2)

def mintBlock(app):
    app.minting = True
    minter = app.chain.lottery()
    msg = f'''Minter chosen!
---------------------------------------------------------------------------------------------------------
Address: {minter}
---------------------------------------------------------------------------------------------------------
Minter will now process {len(app.txsPool)} transctions...'''
    print(msg)

    # decide whether this is a 'cheating' minter but don't make human user cheat
    if (random.random() < Params.CHEAT_CHANCE) and (minter != app.userAddress):
        newBlock = app.chain.cheatMint(app.txsPool, minter)
    else:
        newBlock = app.chain.mint(app.txsPool, minter)


    # case when minter cheated by validating bad txs or altering the list 
    if (confirmTxs(app.txsPool, newBlock.txs, app.chain) == False):
        print('Minter Cheated! Their block was rejected, their stake was revoked, and the current Transaction Pool is preserved...')

        # remove minter's stake as a punishment
        app.chain.validators.pop(minter)

    # make sure our previous hash is correct    
    elif (newBlock.prevHash != app.chain.blocks[-1].hash):
        print('Previous Hash incorrect! This block was rejected and the current Transaction Pool is preserved...')

    else: # minter did not cheat, so we can accept this block
        app.chain.addBlock(newBlock)
        validTxs = newBlock.txs
        good, bad = len(validTxs) - 1, len(app.txsPool) - (len(validTxs)-1) # don't count coinbase reward
        successTxt = "Mint Successful, added Block with %d accepted and %d rejected Transactions"%(good, bad)
        print(successTxt)
        app.txsPool = [] # reset pool to empty 
        app.currTxsPool = [] 
        resetMintPage(app)
        updateUserTxs(app, app.chain.blocks[-1]) # updates app.humanUserTxs dict with txs in this block involving human users
        moveBlockIndex(app, 0) # refresh our current blocks to update with newly created
    app.minting = False

# checks the validity of a blocks transactions versus the known ones in the app.txsPool
def confirmTxs(txsPool, blockTxs, chain):
    # check the coinbase tx seperately
    coinbaseTx, blockTxs = blockTxs[0], blockTxs[1:]

    # compute the valid txs from current pool, and determine whether the
    # block's non coinbase txs are the same by using the hash based verification merkle() method
    validPoolTxs = Block.validTxs(txsPool, chain)
    validPoolTxsHashes = Block.hashList(validPoolTxs)
    validPoolTxsMerkle = Block.merkle(validPoolTxsHashes)
    newBlockTxsMerkle = Block.merkle(Block.hashList(blockTxs))

    if newBlockTxsMerkle != validPoolTxsMerkle:
        print("Minter's Txs list was tampered with!")
        return False
    
    # get reward for valid txsPool transactions
    poolTxsReward = Block.totalReward(validPoolTxs)
    if poolTxsReward != coinbaseTx.amt:
        print("Minter's coinbase reward is incorrect!")
        return False
    return True

################################################################################
#                           Human User Functions
################################################################################

# adds any txs involving a human user to the corresponding value list in app.humanUserTxs
def updateUserTxs(app, block):
    for tx in block.txs:
        # check each humanUser
        for address in app.humanUserTxs:
            if (tx.senderKey == address) or (tx.receiver == address):
                app.humanUserTxs[address] = app.humanUserTxs[address] + [tx]
    currUserTxs = app.humanUserTxs[app.userAddress]
    maxRecentViewable = min(app.txWidth, len(currUserTxs))
    app.currRecentTxs = currUserTxs[0:maxRecentViewable] # currently viewable transactions


# returns list of txs from the chain that involve given user
def myTxs(app, user):
    address = user.rawPubk
    txs = []
    for block in app.chain.blocks:
        for tx in block.txs:
            if tx.senderKey == address or tx.receiver == address:
                txs.append(tx)
    return txs


if __name__ == '__main__':
    runApp(width=725, height=600)