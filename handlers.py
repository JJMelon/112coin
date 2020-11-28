import math

def tutorialKeyHandler(app, event):
    pass

def overviewKeyHandler(app, event):
    pass

def sendKeyHandler(app, event):
    pass

def mintKeyHandler(app, event):
    pass

def recentKeyHandler(app, event):
    if event.key == 'Down':
        moveRecentIndex(app, 1)
    elif event.key == 'Up':
        moveRecentIndex(app, -1)
    elif event.key == "s":
        moveRecentIndex(app, -app.index)

def moveRecentIndex(app, Dir):
    txsCount = len(app.myTxs)
    maxViewable = min(app.txWidth, txsCount)
    app.index += Dir
    if app.txWidth > maxViewable:
        app.index += Dir
    if app.index < 0:
        app.index = 0
    elif app.index > txsCount - app.txWidth:
        app.index = txsCount - app.txWidth
    app.currTxs = app.myTxs[app.index: app.index + app.txWidth]

def viewKeyHandler(app, event):
    pass

def navBarClickHandler(app, event):
    if event.y > app.topMargin:
        return
    boxWidth = app.width/len(app.pages)
    pageClicked = math.floor(event.x/boxWidth)
    app.page = pageClicked

def tutorialClickHandler(app, event):
    pass

def overviewClickHandler(app, event):
    pass

def sendClickHandler(app, event):
    pass

def mintClickHandler(app, event):
    pass

def recentClickHandler(app, event):
    pass

def viewClickHandler(app, event):
    pass
