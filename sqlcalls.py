# Alexander Penney 2020 

import sqlite3, json
import time, random, linecache

from blockchain import BlockChain
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

#creates a transaction object with randomally generated params
def createTx():
    current = time.asctime(time.localtime(time.time()))
    amt = random.randint(1, 20)
    lines = 237 #number of lines in our username file
    sender = linecache.getline('usernames.txt', random.randint(1,lines))
    #make sure receiver is not same as sender
    while True:
        receiver = linecache.getline('usernames.txt', random.randint(1,lines))
        if receiver != sender: break
    sender = sender[:-1]
    receiver = receiver[:-1]
    return (sender, receiver, amt, current)

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
        result = c.fetchone()
        database.commit()
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print(msg)
        if fetch:
            return result 

def getBlockJSON(height):
    # we fetch our id from the height+1 because of starting at 1 in the db
    query = "SELECT * FROM blocks WHERE id = %s" %(height+1)
    rawString = sqlTransaction(query, fetch=True)[1]
    d = json.loads(rawString)
    return d

def insertBlock(block):
    msg = "Inserted Block into chain.db!"
    query = "INSERT INTO blocks (block) VALUES ('%s')" %block.rawString
    print(query)
    sqlTransaction(query, msg)

# def insertTx(tx, c):
#     sender, receiver, amt, time = tx
#     c.execute("INSERT INTO txs (sender, receiver, amt, time) VALUES (?, ?, ?, ?)", (sender, receiver, amt, time))

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
            print("The %s was Dropped!"%table)

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

def updateMaxIndex(app, c):
    c.execute("SELECT MAX(id) FROM txs")
    app.txCount = c.fetchone()[0]
