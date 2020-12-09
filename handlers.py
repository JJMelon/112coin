# Mouse Pressed, Key Pressed, Mouse Moved handler functions

import math, time
from blockchain import Params

def tutorialKeyHandler(app, event):
    pass

def overviewKeyHandler(app, event):
    if event.key == 's':
        try:
            stake = round(float(app.getUserInput("Enter stake amount: ")), 2)
            return app.chain.addStake(app.userAddress, stake)
        except Exception as error:
            print(error)

def sendKeyHandler(app, event):
    pass

def mintKeyHandler(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)
    elif event.key == 'e':
        moveIndex(app, 1000) # move an amount greater than any txs list will be
    elif event.key == 'c':
        index = app.currTxBox
        if index != -1:
            address = app.currPoolTxs[index].senderKey
            app.copy2Clip(address)
    elif event.key == 'r':
        index = app.currTxBox
        if index != -1:
            address = app.currPoolTxs[index].receiver
            app.copy2Clip(address)

def recentKeyHandler(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)
    elif event.key == 'e':
        moveIndex(app, 1000) # move an amount greater than any txs list will be
    elif event.key == 'c':
        index = app.currTxBox
        if index != -1:
            address = app.currRecentTxs[index].senderKey
            app.copy2Clip(address)
    elif event.key == 'r':
        index = app.currTxBox
        if index != -1:
            address = app.currRecentTxs[index].receiver
            app.copy2Clip(address)

# moves the start tx index in the list of txs shown
def moveIndex(app, Dir):
    if app.page == 1 or app.page == 2: # don't worry about moving on these pages
        return
    if app.page == 3: # mint page
        txsCount = len(app.txsPool)
        maxViewable = min(txsCount, app.txsPoolWidth)
        txWidth = app.txsPoolWidth
    elif app.page == 4: # recent page
        txsCount = len(app.humanUserTxs[app.userAddress])
        maxViewable = min(app.txWidth, txsCount)
        txWidth = app.txWidth
    elif app.page == 5: # block viewing page
        currBlockTxs = app.currBlocks[app.blockTxsIndex].txs
        txsCount = len(currBlockTxs)
        maxViewable = min(app.txWidth, txsCount)
        txWidth = app.txWidth
    
    # only move if not all transactions are viewable
    if not (txWidth > maxViewable):
        app.index += Dir
        if app.index < 0:
            app.index = 0
        elif app.index > txsCount - txWidth:
            app.index = txsCount - txWidth

    # refresh our stored current txs, we can call moveIndex(app, 0) to do this function without moving index
    if app.page == 3:
        app.currPoolTxs = app.txsPool[app.index: app.index + app.txsPoolWidth]
    elif app.page == 4:
        app.currRecentTxs = app.humanUserTxs[app.userAddress][app.index: app.index + app.txWidth]
    elif app.page == 5:
        app.currBlockTxs = currBlockTxs[app.index: app.index + app.txWidth]

# TODO fix list index out of range bug when < 3 blocks exist in chain 
def viewKeyHandler(app, event):
    if app.viewingBlockTxs:
        viewBlockTxsKeyHandler(app, event)
    elif event.key == 's':
        moveBlockIndex(app, -len(app.chain.blocks))
    elif event.key == 'e':
        moveBlockIndex(app, len(app.chain.blocks))
    elif event.key == '1':
        app.viewingBlockTxs = True
        app.blockTxsIndex = 0
        moveIndex(app, 0)
    elif event.key == '2':
        if len(app.chain.blocks) < 2:
            return
        app.viewingBlockTxs = True
        app.blockTxsIndex = 1
        moveIndex(app, 0)
    elif event.key == "3":
        if len(app.chain.blocks) < 3:
            return
        app.viewingBlockTxs = True
        app.blockTxsIndex = 2
        moveIndex(app, 0)

def viewBlockTxsKeyHandler(app, event):
    if event.key == '0':
        app.viewingBlockTxs = False
    elif event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)
    elif event.key == 'e':
        moveIndex(app, 1000) # move an amount greater than any txs list will be
    elif event.key == 'c':
        index = app.currTxBox
        if index != -1:
            address = app.currBlockTxs[index].senderKey
            app.copy2Clip(address)
    elif event.key == 'r':
        index = app.currTxBox
        if index != -1:
            address = app.currBlockTxs[index].receiver
            app.copy2Clip(address)

def moveBlockIndex(app, Dir):
    blockCount = len(app.chain.blocks)
    maxViewable = min(app.blockWidth, blockCount)
    app.blockIndex += Dir
    if app.blockWidth > maxViewable:
        app.blockIndex = 0 # we dont have enough blocks to fill screen, so dont move index
    elif app.blockIndex < 0:
        app.blockIndex = 0
    elif app.blockIndex > blockCount - app.blockWidth:
        app.blockIndex = blockCount - app.blockWidth
    app.currBlocks = app.chain.blocks[app.blockIndex: app.blockIndex + app.blockWidth]

def navBarClickHandler(app, event):
    if event.y > app.topMargin:
        return
    if (not app.runningAI):
        app.showMessage('Error', 'Please start the simulation first!')
        return
    boxWidth = app.width/len(app.pages)
    pageClicked = math.floor(event.x/boxWidth)
    app.page = pageClicked
    app.index = 0

def tutorialClickHandler(app, event):
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.tutorialButton
    inButton1 = (B1X0 <= event.x <= B1X1) and (B1Y0 <= event.y <= B1Y1)

    B1X0, B2Y0, B2X1, B2Y1, text2 = app.startButton
    inButton2 = (B1X0 <= event.x <= B2X1) and (B2Y0 <= event.y <= B2Y1)
    if inButton1:
        msg = """Proof of Stake (PoS) protocol states that a person can validate block transactions according to how many coins they hold. 
This means that the more coin owned by a validator the more validating power they have.

POS was created as an alternative to Proof of Work (POW), which is the original consensus 
algorithm in Blockchain technology, used to confirm transactions and add new blocks to the chain.

POW requires huge amounts of energy, with miners needing to sell their coins to ultimately foot the
bill while POS requires much less energy and instead requires a greater initial investment in the form of a stake.

POS is also seen as less risky in terms of the potential for miners to attack the network, as it structures 
compensation in a way that makes an attack less advantageous for the miner."""
        app.showMessage('Learn More', msg)
    elif inButton2 and (not app.runningAI):
        app.runningAI = True
        app.generating = True
        msg = """###############################################################
                     AI SIMULATION HAS STARTED
###############################################################"""
        print(msg)
        app.page = 1

def overviewClickHandler(app, event):
    pass

def sendClickHandler(app, event):
    # button clicks 
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.sendButton1
    B2X0, B2Y0, B2X1, B2Y1, text2 = app.sendButton2
    B3X0, B3Y0, B3X1, B3Y1, text3 = app.sendButton3
    inButton1 = (B1X0 <= event.x <= B1X1) and (B1Y0 <= event.y <= B1Y1)
    inButton2 = (B2X0 <= event.x <= B2X1) and (B2Y0 <= event.y <= B2Y1)
    inButton3 = (B3X0 <= event.x <= B3X1) and (B3Y0 <= event.y <= B3Y1)
    if inButton1:
        app.recAddress = app.getUserInput("Receiver Address:")
    elif inButton2:
        app.sendAmount = app.getUserInput("Enter an amount:")
    elif inButton3:
        receiver = app.recAddress
        try:
            amt = round(float(app.sendAmount), 2)
            sendTx = app.currUser.send(receiver, amt)
            app.txsPool.append(sendTx)
            app.showMessage('Send Message', f'Transaction Sent to Pool!')
            
            # refresh our mint page if we are on it
            app.index = 0
            maxPoolViewable = min(app.txsPoolWidth, len(app.txsPool))
            app.currPoolTxs = app.txsPool[0:maxPoolViewable]
        except Exception as error:
            print(error)
            app.showMessage('Send Error', 'Please enter a number!')

def mintClickHandler(app, event):
    txTableClickHandler(app, event)

def recentClickHandler(app, event):
    txTableClickHandler(app, event)

def txTableClickHandler(app, event):
    if app.page == 3:
        topPad = 60 # extra space given on mintPage
        txWidth = app.txsPoolWidth
        txStart = app.topMargin + app.topPad + topPad
        txBoxHeight = (app.height - (2*app.topMargin + topPad))//txWidth
        txEnd = app.height-app.topMargin
    else:
        txWidth = app.txWidth
        txBoxHeight = (app.height - 2*app.topMargin)//txWidth
        txStart = app.topMargin + app.topPad
        txEnd = app.height-app.topMargin

    # we are inside a transaction box
    if (event.y > txStart) and (event.y < txStart + app.txWidth*txBoxHeight):
        box = math.floor((event.y - txStart)/txBoxHeight)
        # select correct currTxs List
        if app.page == 3:
            txs = app.currPoolTxs
            status = 'Pending Confirmation'
        if app.page == 4:
            txs = app.currRecentTxs
            status = 'Confirmed to Block'
        elif app.page == 5:
            txs = app.currBlockTxs
            status = 'Confirmed to Block'
        
        # ignore case when box # is more than len(txs)
        if box >= len(txs):
            return

        # check if it's already selected, if so then load popup
        if app.currTxBox == box:
            tx = txs[box]
            formatDate = time.asctime(time.localtime(tx.date))
            if tx.senderKey == 'coinbase':
                msg = f'''Status: {status}\nDate: {formatDate}\nSource: Minted\nTo: {tx.receiver}\nCredit: {tx.amt}\nID: {tx.hash}'''
            else:
                msg = f'''Status: {status}\nDate: {formatDate}\nSender: {tx.senderKey}\nTo: {tx.receiver}\nAmount: {tx.amt}\nFee: {Params.TX_FEE}
Net Amount: {tx.amt + Params.TX_FEE}\nID: {tx.hash}'''
            app.showMessage('Transaction', msg)
        app.currTxBox = box
    else:
        app.currTxBox = -1 # if its -1 we don't highlight any of the boxes


    

def viewClickHandler(app, event):
    # load individual messageBox popup for specific tx clicked
    if app.viewingBlockTxs:
        txTableClickHandler(app, event)
    elif event.y > app.topMargin:
        if event.x < app.sideMargin*3:
            moveBlockIndex(app, -1)
        elif event.x > app.width - 3*app.sideMargin:
            moveBlockIndex(app, +1)

def tutorialMouseHandler(app, event):
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.tutorialButton
    inButton1 = (B1X0 <= event.x <= B1X1) and (B1Y0 <= event.y <= B1Y1)
    if inButton1 and (app.tutorialButtonColor == 'gold'):
        app.tutorialButtonColor = app.dGold
    elif (not inButton1) and (app.tutorialButtonColor == app.dGold):
        app.tutorialButtonColor = 'gold'
    
    B2X0, B2Y0, B2X1, B2Y1, text2 = app.startButton
    inButton2 = (B2X0 <= event.x <= B2X1) and (B2Y0 <= event.y <= B2Y1)
    if inButton2 and (app.startButtonColor == 'gold'):
        app.startButtonColor = app.dGold
    elif (not inButton2) and (app.startButtonColor == app.dGold):
        app.startButtonColor = 'gold'

def sendMouseHandler(app, event):
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.sendButton1
    B2X0, B2Y0, B2X1, B2Y1, text2 = app.sendButton2
    B3X0, B3Y0, B3X1, B3Y1, text3 = app.sendButton3
    inButton1 = (B1X0 <= event.x <= B1X1) and (B1Y0 <= event.y <= B1Y1)
    inButton2 = (B2X0 <= event.x <= B2X1) and (B2Y0 <= event.y <= B2Y1)
    inButton3 = (B3X0 <= event.x <= B3X1) and (B3Y0 <= event.y <= B3Y1)
    if app.sendButton1Color == 'gold' and inButton1:
        app.sendButton1Color = app.dGold
    elif app.sendButton1Color == app.dGold and not inButton1:
        app.sendButton1Color = 'gold'
    
    elif app.sendButton2Color == 'gold' and inButton2:
        app.sendButton2Color = app.dGold
    elif app.sendButton2Color == app.dGold and not inButton2:
        app.sendButton2Color = 'gold'

    elif app.sendButton3Color == 'gold' and inButton3:
        app.sendButton3Color = app.dGold
    elif app.sendButton3Color == app.dGold and not inButton3:
        app.sendButton3Color = 'gold'