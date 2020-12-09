# Draw functions file

import time, math
from cmu_112_graphics import ImageTk


# takes time in seconds since epoch and returns short version string MM/DD/YY-HH:MM:SS
def formatTime(Time):
    struct = time.localtime(Time)
    return time.strftime("%m/%d/%y--%H:%M:%S", struct)


################################################################################
#                           Navigation Bar
################################################################################
def drawNavbar(app, canvas):
    boxWidth = (app.width)/len(app.pages)
    boxHeight = app.topMargin
    for i in range(len(app.pages)):
        name = app.pages[i]
        color = 'white'
        if app.page == i:
            color = 'lightGrey'
        x0, y0 = i*boxWidth, 0
        x1, y1 = x0+boxWidth, boxHeight
        mid = (x0+x1)/2
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=1)
        canvas.create_text(mid, boxHeight/2, text=name, font='Arial 10 bold')


################################################################################
#                                Tutorial Page
################################################################################

def drawTutorial(app, canvas):
    topPad = 20
    font = 'Arial 10'
    Y0 = app.topMargin + topPad
    canvas.create_text(app.width/2, Y0, text='112Coin Tutorial',
        font='Arial 24 bold')
    Y1 = Y0 + 40
    intro = """This application simulates a Proof of Stake based Cryptocurrency with over 50 other AI users.
But what is a Cryptocurrency?"""
    canvas.create_text(app.sideMargin, Y1, text=intro, anchor='nw', font=font)
    Y2 = Y1 + 60
    crypto = """Cryptocurrency is an internet-based medium of exchange which uses cryptographical functions to conduct financial 
transactions. Cryptocurrencies leverage blockchain technology to gain decentralization, transparency, and 
immutability. The most important feature of a cryptocurrency is that it is not controlled by any central authority: 
the decentralized nature of the blockchain makes cryptocurrencies theoretically immune to the old ways of government 
control and interference. Cryptocurrencies can be sent directly between two parties via the use of private and public 
keys. These transfers can be done with minimal processing fees, allowing users to avoid the steep fees charged by 
traditional financial institutions."""
    canvas.create_text(app.sideMargin, Y2, text=crypto, anchor='nw', font=font)

    blockchain = """Blockchain is a specific type of database that differs from others in the way it stores information; 
blockchains store data in blocks that are then chained together. As new data comes in it is incoporated into a new block. 
Once the block is filled with data it is 'chained' to the previous block by using such blocks hash, a unique identifer. 
Different types of information can be stored on a blockchain but in this application it has been used as a ledger for 
transactions. Many blockchains are decentralized, meaning they are stored by many individuals, making them immutable.""" 
    Y3 = Y2 + 160
    canvas.create_text(app.sideMargin, Y3, text=blockchain, anchor='nw', font=font)

    # learn more proof of stake button
    x0, y0, x1, y1, text1 = app.tutorialButton
    color1 = app.tutorialButtonColor
    canvas.create_rectangle(x0, y0, x1, y1, fill=color1, outline='gold', width=3)
    canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text1, fill='white', font='Arial 12 bold')

    Y4 = Y3 + 100
    this = """In this application, you start with 10 112Coin and can send coin to other AI users, earn coin from minting new
blocks, and stake coin to increase your chance of winning the minting lottery and receiving the mint reward. You can also 
view all minted blocks and their transactions as well as the current pending transactions and those involving you."""
    canvas.create_text(app.sideMargin, Y4, text=this, anchor='nw', font=font)

    # start the simulation button
    x0, y0, x1, y1, text2 = app.startButton
    color2 = app.startButtonColor
    canvas.create_rectangle(x0, y0, x1, y1, fill=color2, outline='gold', width=3)
    canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text2, fill='white', font='Arial 20 bold')


################################################################################
#                                Overview Page
################################################################################

def drawOverview(app, canvas):
    leftMargin = 20
    topPad = 20
    boxHeight, boxWidth = 40, 300
    boxX0, boxY0 = app.width/2-boxWidth/2, app.topMargin + 7.5*topPad
    boxX1, boxY1 = boxX0 + boxWidth, boxY0 + boxHeight
    canvas.create_text(leftMargin, app.topMargin + topPad, text=f"Balance: {app.chain.accounts[app.userAddress]}", font='Arial 18 bold', anchor='nw')
    canvas.create_text(leftMargin, app.topMargin + 2.5*topPad, text=f'Public Key: {app.userAddress[0:80]}...', 
                                            font='Arial 10', anchor='nw')
    canvas.create_text(leftMargin, app.topMargin + 4*topPad, text=f'Private Key: {app.currUser.rawPrivk}', 
                                            font='Arial 10', anchor='nw')


    # User's stake information
    canvas.create_text(app.width/2, app.topMargin + 6*topPad, text='Your Stake',
             font='Arial 18 bold')
    imgSize = app.coinImg.size[0]
    canvas.create_image(boxX0-imgSize, (boxY0 + boxY1)/2, image=ImageTk.PhotoImage(app.coinImg))
    canvas.create_image(boxX1+imgSize, (boxY0 + boxY1)/2, image=ImageTk.PhotoImage(app.coinImg))
    
    
    # stake info box 
    amt, startTime = app.chain.validators.get(app.userAddress, (None, None))
    
    # if we are a validator and have an active stake
    if startTime != None:
        timeLeft = (startTime + app.stakeDuration) - time.time()
        Text = 'Amt: %0.2f | Time Left: %ds' % (amt, timeLeft)
        color = 'darkGreen'
        fill = app.lGreen
    else:
        Text = 'No Active Stake!'
        amt = 0
        color='red'
        fill = 'red'

    canvas.create_rectangle(boxX0, boxY0, boxX1, boxY1, width=2, fill=fill)
    canvas.create_text((boxX1+boxX0)/2, (boxY1+boxY0)/2, text=Text,
            font='Arial 12 bold', fill='white')

    canvas.create_text(app.width/2, boxY1 + topPad, text='Press s to stake coin!',
             font='Arial 18 bold')

    # total staked
    font2 = 'Arial 16 bold'
    canvas.create_text(app.width/2, app.height - 12*topPad, text='Validator Statistics', font='Arial 20 bold')
    canvas.create_text(app.width/2, app.height - 10*topPad, text=f'Total Staked: {app.chain.staked} (112Coin)',
        font=font2, fill=app.mGreen)

    # top staker
    canvas.create_text(app.width/2, app.height - 8*topPad, text=f'Top Staker Address: {app.topStaker[0:20]}...',
        font=font2, fill=app.mGreen)
    canvas.create_text(app.width/2, app.height - 6*topPad, text=f'Top Staker Amount: {app.topStake} (112Coin)',
        font=font2, fill=app.mGreen)

    # your share of total
    gap = 25
    txt1X0 = app.width/2 + 125
    canvas.create_text(txt1X0, app.height-3*topPad, text='Your Share of Staked Coin:',
            font='Arial 18 bold', anchor='e')
    try:
        percent = round(amt/app.chain.staked*100, 2)
    except:
        percent = 0
    canvas.create_text(txt1X0 + gap, app.height-3*topPad, text=f'{percent}%',
            font='Arial 18 bold', fill=color, anchor='w')



################################################################################
#                                Send Page
################################################################################

def drawSend(app, canvas):
    topPad = 10
    boxPad = 5
    canvas.create_text(app.width/2, app.topMargin + topPad, text="Send coin to a user's address.",
             font='Arial 18 bold', anchor='n')
    
    # button to enter receiver user address
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.sendButton1
    color1 = app.sendButton1Color
    canvas.create_rectangle(B1X0, B1Y0, B1X1, B1Y1, width=2, fill=color1, outline='gold')
    canvas.create_text((B1X0+B1X1)/2,(B1Y0+B1Y1)/2, text=text1, font='Arial 12 bold', fill='white')
    # receiver userAddress field
    boxHeight, boxWidth = 25, (app.width-app.sideMargin - B1X0)
    boxX0, boxY0 = B1X0, B1Y0 - boxHeight - boxPad
    boxX1, boxY1 = boxX0 + boxWidth, boxY0 + boxHeight
    canvas.create_rectangle(boxX0, boxY0, boxX1, boxY1, width='2')
    canvas.create_text(boxX0 + boxPad, (boxY0 + boxY1)/2, text=f'Receiver:', 
        font='Arial 14 bold', anchor='w')
    canvas.create_text(boxX0 + 100, (boxY0 + boxY1)/2, text=f'{str(app.recAddress)[0:60]}...', 
        font='Arial 12', anchor='w')

    # button to enter amt to send
    color2 = app.sendButton2Color
    B2X0, B2Y0, B2X1, B2Y1, text2 = app.sendButton2
    canvas.create_rectangle(B2X0, B2Y0, B2X1, B2Y1, width=2, fill=color2, outline='gold')
    canvas.create_text((B2X0 + B2X1)/2,(B2Y0 + B2Y1)/2, text=text2, font='Arial 12 bold', fill='white')
    # tx amount field
    boxHeight, boxWidth = 25, 150
    boxX0, boxY0 = B2X0, B2Y0 - boxHeight - boxPad
    boxX1, boxY1 = boxX0 + boxWidth, boxY0 + boxHeight
    canvas.create_rectangle(boxX0, boxY0, boxX1, boxY1, width='2')
    canvas.create_text(boxX0 + boxPad, (boxY0 + boxY1)/2, text=f'Amount:', 
        font='Arial 14 bold', anchor='w')
    canvas.create_text(boxX0 + boxWidth-65, (boxY0 + boxY1)/2, text=app.sendAmount, 
        font='Arial 12', anchor='w')
    
    # image
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.sendImg))
    # button to confirm send transaction
    color3 = app.sendButton3Color
    B3X0, B3Y0, B3X1, B3Y1, text3 = app.sendButton3
    canvas.create_rectangle(B3X0, B3Y0, B3X1, B3Y1, width=2, fill=color3)
    canvas.create_text((B3X0+B3X1)/2,(B3Y0+B3Y1)/2, text=text3, 
            font='Arial 12 bold', fill='white')

    # balance info at bottom
    canvas.create_text(app.width/2, app.height-100, text=f"Balance: {app.chain.accounts[app.userAddress]}", font='Arial 18 bold')

    # tip
    canvas.create_text(app.width/2, app.height-50, text='Try copying an address from the view pages!',
            font='Arial 10', fill='darkGreen')


################################################################################
#                                Mint Page
################################################################################

def drawMint(app, canvas):
    topPad = 20
    canvas.create_text(app.sideMargin, app.topMargin + 3*topPad/2, 
        text='Transaction Pool', anchor='w', font='Arial 20 bold')

    canvas.create_text(app.width - app.sideMargin - 110, app.topMargin + topPad, 
        text='Current Block Reward: ', anchor='ne', font='Arial 16 bold')
    canvas.create_text(app.width - app.sideMargin, app.topMargin + topPad, 
        text=f'{app.currReward} (112C)', anchor='ne', font='Arial 16 bold', fill=app.dGold)
    colsX = drawTxColumns(app, canvas, app.topMargin + 3*topPad)
    if len(app.txsPool) == 0:
        canvas.create_image(app.width/2, 2*app.height/3, image=ImageTk.PhotoImage(app.emptyImg))
        canvas.create_text(app.width/2, app.topMargin + 6*topPad, text="No Pending Transactions",
            font='Arial 24 bold', fill=app.grey)
    else:
        drawTxs(app, canvas, colsX, app.currPoolTxs, app.topMargin + app.topPad + 3*topPad)


################################################################################
#                                Recent Page
################################################################################

def drawRecent(app, canvas):
    colsX = drawMyTxColumns(app, canvas)
    drawTxs(app, canvas, colsX, app.currRecentTxs, app.topMargin + app.topPad, myTxs=True)

def drawMyTxColumns(app, canvas):
    topPad = 20
    tableWidth = app.width-2*app.sideMargin
    startY, endY = app.topMargin, app.topMargin + topPad
    color = app.lGreen

    # Date Column
    dateWidth = 2*tableWidth/7
    dateEnd = app.sideMargin + dateWidth
    canvas.create_rectangle(app.sideMargin, startY, dateEnd, endY, fill=color)
    canvas.create_text((app.sideMargin+dateWidth)/2, app.topMargin + topPad/2, text='Date', 
        font="Arial 14 bold", fill='white')

    # Type Column
    typeWidth = tableWidth/7
    typeEnd = app.sideMargin + dateWidth + typeWidth
    canvas.create_rectangle(dateEnd, startY, typeEnd, endY, fill=color)
    canvas.create_text((dateEnd+typeEnd)/2, app.topMargin + topPad/2, text='Type', 
        font="Arial 14 bold", fill='white')

    # Label Column
    labelWidth = 3*tableWidth/7
    labelEnd = typeEnd + labelWidth
    canvas.create_rectangle(typeEnd, startY, labelEnd, endY, fill=color)
    canvas.create_text((typeEnd+labelEnd)/2, app.topMargin + topPad/2, text='Label', 
        font="Arial 14 bold", fill='white')

    # Amount Column
    amtWidth = tableWidth/7
    amtEnd = labelEnd + amtWidth
    canvas.create_rectangle(labelEnd, startY, amtEnd, endY, fill=color)
    canvas.create_text((labelEnd+amtEnd)/2, app.topMargin + topPad/2, text='Amount', 
        font="Arial 14 bold", fill='white')

    colsX = app.sideMargin, dateEnd, typeEnd, labelEnd
    canvas.create_text(app.width/2, app.height-app.topMargin/2, text="Up/Down to move, s to go to start, e to go to end, c to copy tx sender, r to copy receiver.")
    # tip
    canvas.create_text(app.width/2, app.height-app.topMargin/4, text='Double Click a transaction to see more!', fill='darkGreen',)
    return colsX

def drawMyTx(app, canvas, tx, x0, y0, colsX, color, num):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth 
    txBoxWidth = app.width - 2*app.sideMargin
    canvas.create_rectangle(x0, y0, x0 + txBoxWidth, y0 + txBoxHeight, width=2, fill=color)
    txtCy = y0 + txBoxHeight/2
    sender, receiver, amt, date = tx.senderKey, tx.receiver, tx.amt, tx.date
    date = time.asctime(time.localtime(date))
    # label gives the useful address in the transaction because yours is already a given
    label, txType = 'N/A', 'N/A'
    if sender == "coinbase":
        txType = 'Minted'
        label = receiver
    elif sender == app.userAddress:
        txType = 'Sent To'
        label = receiver
    elif receiver == app.userAddress:
        txType = 'Received'
        label = sender

    pad = 10
    dateX, typeX, labelX, amtX = colsX
    # date column
    canvas.create_text(dateX+pad, txtCy, text=(f'{date}'), 
            font='Arial 8 bold', anchor='w')
    
    # type column
    canvas.create_text(typeX+pad, txtCy, text=(f'{txType}'), 
            font='Arial 8 bold', anchor='w')

    # label column
    canvas.create_text(labelX+pad, txtCy, text=(str(label)[0:15]), 
            font='Arial 8 bold', anchor='w')

    # amount column
    canvas.create_text(amtX+pad, txtCy, text=(f'{amt} (112C)'), 
            font='Arial 8 bold', anchor='w')

    # number of transaction in list column
    canvas.create_text(app.sideMargin - 10, txtCy, text=f'{app.index + num}')

################################################################################
#                                View Chain Page
################################################################################

def drawView(app, canvas):
    # when user presses one of three keys (1,2,3) the transactions for that block are shown in a new draw page
    if app.viewingBlockTxs:
        colsX = drawTxColumns(app, canvas, app.topMargin)
        drawTxs(app, canvas, colsX, app.currBlockTxs, app.topMargin + app.topPad)
    else:
        canvas.create_image(app.width/2, app.topMargin + app.height/10.5, image=ImageTk.PhotoImage(app.chainImg))
        drawBlocks(app, canvas)
        canvas.create_text(app.sideMargin, app.height-50, text='<== Click this side to move\nPress s to go to start', anchor='w')
        canvas.create_text(app.width-app.sideMargin, app.height-50, text='Click this side to move ==>\nPress e to go to end', anchor='e')
        canvas.create_text(app.width/2, app.height-50, text='Block Viewer', font='Arial 22 bold')
        canvas.create_text(app.width/2, app.height-25, text="Press Number Keys 1-3 to see a block's transactions. Press 0 to return.")

def drawBlocks(app, canvas):
    i = 1
    for block in app.currBlocks:
        if i > 3:
            break
        drawBlock(app, canvas, block, i*app.sideMargin + (i-1)*app.blockDrawSize, i)
        i += 1

def drawBlock(app, canvas, block, x0, num):
    yPad = app.height/5
    blockBoxHeight = app.height - (app.topMargin + 2*yPad)
    x1 = x0+app.blockDrawSize
    y0 = app.topMargin + yPad
    y1 = y0 + blockBoxHeight
    color = '#FFFF8F'
    canvas.create_rectangle(x0, y0, x1, y1, width=3, fill=color)
    height = app.chain.blocks.index(block)

    heightY, timeY, minterY = 30, 5, 50
    prevHashY, hashY = y1 - 40, y1 - 70
    heightX = timeX = app.blockDrawSize/2
    minterX = prevHashX = hashX = 5
    canvas.create_text(x0 + heightX, y0 + heightY, text=f'Block: {height}', font='Arial 12 bold')
    canvas.create_text(x0 + timeX, y0 + timeY, text=formatTime(block.time), anchor='n', font='Arial 8')
    canvas.create_text(x0 + minterX, y0 + minterY, text=f'Minter: {block.minter[0:20]}', anchor='nw', font='Arial 10 bold')

    prevText = str(block.prevHash)[0:30] + '...'
    if block.prevHash == '0':
        prevText = 'None'
    canvas.create_text(x0 + prevHashX, prevHashY, text="Pevious Block's Hash:", anchor='nw', font='Arial 10 bold')
    canvas.create_text(x0 + prevHashX, prevHashY + 15, text=prevText, anchor='nw', font='Arial 8')

    hashText = f'{block.hash[0:30]}...'
    canvas.create_text(x0 + hashX, hashY, text="This Block's Hash: ", anchor='nw', font='Arial 10 bold')
    canvas.create_text(x0 + hashX, hashY + 15, text=hashText, anchor='nw', font='Arial 8')
    yStart, yEnd = y0 + minterY + 15, y1 - 85

    # brief transactions list appearing in each block rectangle
    drawBriefTxs(app, canvas, block.txs[0:3], x0, yStart, x1, yEnd)

    # number below each block
    canvas.create_text((x0 + x1)/2, y1 + 15, text=num, font='Arial 18 bold')

def drawBriefTxs(app, canvas, txs, x0, y0, x1, y1):
    if txs == []:
        canvas.create_text((x0+x1)/2, (y0+y1)/2, text='No Transactions!', font='Arial 18 bold')
    txBoxHeight = (y1-y0)/3
    for i in range(len(txs)):
        yStart = y0 + i*txBoxHeight
        yEnd = yStart + txBoxHeight
        txtCy = (yStart + yEnd)/2

        canvas.create_rectangle(x0, yStart, x1, yEnd, width=2, fill='gold')
        tx = txs[i]
        tableWidth = (x1-x0)
        
        # sender column
        sendWidth = 3*tableWidth/7
        sendEnd = x0 + 10 + sendWidth
        senderTxt = str(tx.senderKey)[0:10] + '...=>'
        canvas.create_text(x0 + 10, txtCy, text=senderTxt, 
                font='Arial 8', anchor='w')

        # receiver column
        recWidth = 3*tableWidth/7
        recEnd = sendEnd + recWidth
        receiverTxt = str(tx.receiver)[0:10] + '...'
        canvas.create_text(sendEnd, txtCy, text=receiverTxt, 
                font='Arial 8', anchor='w')

        # amount column
        amtWidth = tableWidth/7
        canvas.create_text(recEnd-10, txtCy, text=tx.amt, font='Arial 8 bold', anchor='w')

def drawTxColumns(app, canvas, startY):
    topPad = 20
    tableWidth = app.width-2*app.sideMargin
    endY = startY + topPad
    color = app.lGreen

    # Date Column
    dateWidth = 2*tableWidth/11
    dateEnd = app.sideMargin + dateWidth
    canvas.create_rectangle(app.sideMargin, startY, dateEnd, endY, fill=color)
    canvas.create_text((app.sideMargin+dateWidth)/2, startY + topPad/2, text='Date', 
        font="Arial 14 bold", fill='white')

    # Sender Column
    sendWidth = 4*tableWidth/11
    sendEnd = app.sideMargin + dateWidth + sendWidth
    canvas.create_rectangle(dateEnd, startY, sendEnd, endY, fill=color)
    canvas.create_text((dateEnd+sendEnd)/2, startY + topPad/2, text='Sender',
         font="Arial 14 bold", fill='white')

    # Receiver Column
    recWidth = 4*tableWidth/11
    recEnd = sendEnd + recWidth
    canvas.create_rectangle(sendEnd, startY, recEnd, endY, fill=color)
    canvas.create_text((sendEnd+recEnd)/2, startY + topPad/2, text='Label', 
        font="Arial 14 bold", fill='white')

    # Amount Column
    amtWidth = tableWidth/11
    amtEnd = recEnd + amtWidth
    canvas.create_rectangle(recEnd, startY, amtEnd, endY, fill=color)
    canvas.create_text((recEnd+amtEnd)/2, startY + topPad/2, text='Amt', 
        font="Arial 14 bold", fill='white')

    colsX = app.sideMargin, dateEnd, sendEnd, recEnd
    canvas.create_text(app.width/2, app.height-app.topMargin/2, text="Up/Down to move, s to go to start, e to go to end, c to copy tx sender, r to copy receiver.")
    # tip
    canvas.create_text(app.width/2, app.height-app.topMargin/4, text='Double Click a transaction to see more!', fill='darkGreen')
    return colsX


################################################################################
#                 Transactions Pages (For Recent and Individual Blocks)
################################################################################

def drawTxs(app, canvas, colsX, txs, startY, myTxs=False):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth
    if app.index%2 == 0:
        colorMode = 0
    else:
        colorMode = 1
    for i in range(len(txs)):
        # makes color unchangable when there are less than 10 txs, removing weird changing color effect
        if len(txs) < app.txWidth:
            colorMode = 0
        if colorMode == 1:
            if i%2 == 0:
                color = 'lightGrey'
            else:
                color = 'white'
        else:
            if i%2 == 0:
                color = 'white'
            else:
                color = 'lightGrey'
        if i == app.currTxBox:
            color = 'gold'
        tx = txs[i]
        x0, y0 = app.sideMargin, startY + i*txBoxHeight
        if myTxs:
            drawMyTx(app, canvas, tx, x0, y0, colsX, color, i)
        else:
            drawTx(app, canvas, tx, x0, y0, colsX, color, i)

def drawTx(app, canvas, tx, x0, y0, colsX, color, num):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth 
    txBoxWidth = app.width - 2*app.sideMargin
    canvas.create_rectangle(x0, y0, x0 + txBoxWidth, y0 + txBoxHeight, width=2, fill=color)
    txtCy = y0 + txBoxHeight/2
    sender, receiver, amt, date = str(tx.senderKey), str(tx.receiver), str(tx.amt), tx.date
    if sender == app.userAddress:
        sender = 'You'
    if receiver == app.userAddress:
        receiver = 'You'
    date = formatTime(date)
    pad = 10
    dateX, typeX, labelX, amtX = colsX
    
    # date column
    canvas.create_text(dateX+pad, txtCy, text=(f'{date}'), 
            font='Arial 8 bold', anchor='w')
    
    # sender column
    canvas.create_text(typeX+pad, txtCy, text=sender[0:30], 
            font='Arial 8 bold', anchor='w')

    # receiver column
    canvas.create_text(labelX+pad, txtCy, text=receiver[0:30], 
            font='Arial 8 bold', anchor='w')

    # amount column
    canvas.create_text(amtX, txtCy, text=(amt + ' (112C)'), 
            font='Arial 8 bold', anchor='w')
    
    # number of transaction in list column
    canvas.create_text(app.sideMargin - 10, txtCy, text=f'{app.index + num}')